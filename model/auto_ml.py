import pandas as pd
from utils.logger_config import logger
from omegaconf import OmegaConf
import json
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score, f1_score
from autogluon.tabular import TabularPredictor
from imblearn.over_sampling import SMOTE  # SMOTE 라이브러리 임포트
from model.regression_metrics import adjusted_r2_score
from optimization.feature_optimization import convert_to_serializable

def automl_module(data, task, target, preset, time_to_train, config):
    """
    Autogluon 라이브러리를 활용하여 자동으로 모델을 실행시킵니다.
    
    Args:
        data (pd.DataFrame): 전처리된 데이터셋
        task (str): 수행할 task ('regression', 'binary', 'multiclass')
        target (str): target feature
        preset (int): 모델의 정도 (0~3 정수값)
        time_to_train (int): 학습 시간 (초 단위)
    
    Raises:
        KeyError: target이 데이터셋에 존재하지 않는 경우 에러 발생
        ValueError: task type이 예상치 못한 경우 에러 발생
    
    Returns:
        predictor(Object): 학습된 모델
        test_df(pd.DataFrame): test에 사용된 데이터셋
    """        
    if task == 'regression':
        train_df, test_df = train_test_split(data, test_size=0.2, random_state=42)
    else:
        train_df, test_df = train_test_split(data, test_size=0.2, random_state=42, stratify=data[target])

    
    if target not in train_df.columns:
        raise KeyError(f"Label column '{target}' is missing from training data. Training data columns: {list(train_df.columns)}")
    
    # (옵션 1) 분류 문제인 경우, SMOTE를 적용하여 클래스 불균형 문제 해결 (수치형 데이터여야 함)
    if task in ['binary', 'multiclass']:
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
        # hyperparameters=hyperparameters,
        # hyperparameter_tune_kwargs=hyperparameter_tune_kwargs, # Bayesian Optimization 적용
        num_gpus=1 # GPU 사용 가능하게 수정
    )

    y_pred = predictor.predict(test_df.drop(columns=[target]))  

    if task == 'regression':
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

    elif task in ['binary', 'multiclass']:
        # 정확도와 F1 스코어를 Python 기본 float 타입으로 변환
        accuracy = float(accuracy_score(test_df[target], y_pred))
        f1 = float(f1_score(test_df[target], y_pred, average='weighted'))


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
    logger.info(f'LeaderBoard Result :\n{leaderboard}')
    config["top_models"] = leaderboard.to_dict()
    
    feature_importance = predictor.feature_importance(test_df)
    logger.info(f'Feature Importance:\n{feature_importance}')
    logger.info('==============================================================\n')
    logger.info('==============================================================\n')
    config["feature_importance"] = feature_importance.to_dict()

    evaluation = predictor.evaluate(test_df)
    logger.info(f'Evaluation Results:\n{evaluation}')
    logger.info('==============================================================\n')
    logger.info('==============================================================\n')
    
    return predictor, test_df, config


def train_model(data, config_path):
    """
    auto_ml을 실행시킵니다.
    
    Args:
        data (pd.DataFrame): 전처리된 데이터셋
        config (dict): 설정값을 포함한 config 파일. 여기에는 task, target_feature, model_quality, time_to_train 등이 포함됨.
    
    Returns:
        model(Object): 학습된 모델
        test_df(pd.DataFrame): test에 사용된 데이터셋
    """
    config = OmegaConf.load(config_path)
    model_config = config['model']
    task = config['task']
    target = config['target_feature']
    selected_quality = model_config['model_quality']
    time_to_train = model_config['time_to_train']
    preset = f'{selected_quality}_quality'
    try:
        model, test_df, config = automl_module(data, task, target, selected_quality, time_to_train, config)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(OmegaConf.to_container(config, resolve=True), f, indent=4, ensure_ascii=False)

        logger.info('AutoGLuon에서 기대하는 클래스\n\n\n\n')
        logger.info(model.class_labels)
        logger.info('\n\n==========================================\n')
    
    except Exception as e:
        logger.error(f"Model training failed: {e}")
        return

    return model, test_df