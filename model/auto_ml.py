import json
import pandas as pd
from omegaconf import OmegaConf
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, accuracy_score, f1_score
from autogluon.tabular import TabularPredictor
from imblearn.over_sampling import SMOTE
from utils.logger_config import logger
from model.regression_metrics import adjusted_r2_score
from optimization.feature_optimization import convert_to_serializable
from typing import Tuple


def automl_module(
        data: pd.DataFrame, task: str, target: str, preset: str, time_to_train: int, config: dict
        ) -> Tuple[TabularPredictor, pd.DataFrame, dict]:
    '''
    Summary:
        AutoGluon을 사용하여 자동으로 모델을 학습하고 평가하는 함수
        AutoGluon의 TabularPredictor를 사용하여 자동 모델 학습 및 평가를 수행함.
        Regression 및 Classification(이진/다중) 문제를 지원.
        분류 문제의 경우 SMOTE를 사용하여 데이터 불균형을 보정.
    
    Args:
        data (pd.DataFrame): 전처리된 데이터셋.
        task (str): 수행할 작업 유형 ('regression', 'binary', 'multiclass').
        target (str): 목표 변수 이름.
        preset (int): 모델의 품질 정도 (예: 'best_quality', 'high_quality' 등).
        time_to_train (int): 학습 시간 (초 단위)
        config (dict): 설정값이 포함된 딕셔너리
    
    Returns:
        Tuple[TabularPredictor, pd.DataFrame, dict]:
            predictor (TabularPredictor): 학습된 모델 객체.
            test_df (pd.DataFrame): 평가에 사용된 테스트 데이터셋.
            config (dict): 모델 학습 결과가 반영된 설정값.
    ''' 
    if task == "regression":
        train_df, test_df = train_test_split(data, test_size=0.2, random_state=42)
    else:
        train_df, test_df = train_test_split(data, test_size=0.2, random_state=42, stratify=data[target])

    
    if target not in train_df.columns:
        raise KeyError(f"Label column '{target}' is missing from training data. Training data columns: {list(train_df.columns)}")
    
    # (옵션 1) 분류 문제인 경우, SMOTE를 적용하여 클래스 불균형 문제 해결 (수치형 데이터여야 함)
    if task in ["binary", "multiclass"]:
        X_train = train_df.drop(columns=[target])
        y_train = train_df[target]
        
        try:
            sm = SMOTE(random_state=42)
            X_res, y_res = sm.fit_resample(X_train, y_train)
            # resampled 데이터를 DataFrame으로 재구성
            train_df = pd.concat([pd.DataFrame(X_res, columns=X_train.columns), 
                                  pd.DataFrame(y_res, columns=[target])], axis=1)
            logger.info("SMOTE를 적용하여 학습 데이터의 클래스 불균형을 보정하였습니다.")
        except Exception as e:
            logger.error(f"SMOTE 적용 중 오류 발생: {e}")
            # SMOTE 실패시 원본 데이터를 사용하도록 함
            pass

    # 모델 학습
    predictor = TabularPredictor(
        label=target,
        problem_type=task,
        verbosity=2   # 튜닝 과정 자세히 보기 위해 verbosity=2 권장 (디폴트는 1)
    ).fit(
        train_data=train_df,
        time_limit=time_to_train,          
        presets=preset,  # 정수 대신 변환된 preset 문자열 사용
        num_gpus=1
    )

    y_pred = predictor.predict(test_df.drop(columns=[target]))  

    if task == "regression":
        mae = mean_absolute_error(test_df[target], y_pred)
        # test_df에서 target 컬럼을 제외한 X 데이터를 구함
        X_test = test_df.drop(columns=[target])
        # Advanced (Adjusted) R^2 계산
        adv_r2 = adjusted_r2_score(test_df[target], y_pred, X_test)
        logger.info("AutoGluon Regressor 결과:")
        logger.info(f" - MAE : {mae:.4f}")
        logger.info(f" - Advanced R^2 : {adv_r2:.4f}")

        config["model_result"] = {
            "MAE": round(mae, 4),
            "Advanced_R2": round(adv_r2, 4)
        }

    elif task in ["binary", "multiclass"]:
        # 정확도와 F1 스코어를 Python 기본 float 타입으로 변환
        accuracy = float(accuracy_score(test_df[target], y_pred))
        f1 = float(f1_score(test_df[target], y_pred, average="weighted"))

        logger.info("AutoGluon Classifier 결과:")
        logger.info(f" - Accuracy : {accuracy:.4f}")
        logger.info(f" - F1 Score : {f1:.4f}")

        config["model_result"] = {
            "accuracy": round(accuracy, 4),
            "f1_score": round(f1, 4)
        }
    else:
        raise ValueError(f"Unsupported task type: {task}")

    leaderboard = predictor.leaderboard(test_df, silent=True)
    logger.info(f"LeaderBoard Result :\n{leaderboard}")

    feature_importance = predictor.feature_importance(test_df)
    logger.info(f"Feature Importance:\n{feature_importance}")
    
    evaluation = predictor.evaluate(test_df)
    logger.info(f"Evaluation Results:\n{evaluation}")
    
    config["top_models"] = leaderboard.to_dict()
    config["feature_importance"] = feature_importance.to_dict()
    
    return predictor, test_df, config


def train_model(data: pd.DataFrame, config_path: str) -> Tuple[TabularPredictor, pd.DataFrame]:
    '''
    Summarys:
        AutoML 모델을 학습시키는 함수.
        설정 파일을 로드하고 AutoML을 실행하여 모델을 학습함.
        학습 완료 후, 설정 파일을 업데이트하여 결과를 저장함.
    
    Args:
        data (pd.DataFrame): 전처리된 데이터셋.
        config_path (str): 설정 파일 (.json)의 경로
    
    Returns:
        Tuple[TabularPredictor, pd.DataFrame]:
            model (TabularPredictor): 학습된 AutoML 모델.
            test_df (pd.DataFrame): 평가에 사용된 테스트 데이터셋.
    '''
    config = OmegaConf.load(config_path)
    model_config = config['model']
    task = config['task']
    target = config['target_feature']
    selected_quality = model_config['model_quality']
    time_to_train = model_config['time_to_train']
    
    try:
        model, test_df, config = automl_module(data, task, target, selected_quality, time_to_train, config)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(OmegaConf.to_container(config, resolve=True), f, indent=4, ensure_ascii=False)

        logger.info('AutoGLuon에서 기대하는 클래스 목록:')
        logger.info(model.class_labels)
    
    except Exception as e:
        logger.error(f"Model training failed: {e}")
        return None, None

    return model, test_df