import pandas as pd
import logging
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score, f1_score
from autogluon.tabular import TabularPredictor
from imblearn.over_sampling import SMOTE  # SMOTE 라이브러리 임포트

def automl_module(data, task, target, preset, time_to_train):
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
    # preset 정수를 문자열 preset으로 변환하는 매핑
    preset_mapping = {
        0: "best_quality",
        1: "high_quality",
        2: "good_quality",
        3: "medium_quality"
    }
    preset_str = preset_mapping.get(preset, "medium_quality")  # 기본값은 medium_quality

    # 데이터 분할 (stratify 옵션을 통해 target 비율 유지)
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
            print("SMOTE를 적용하여 학습 데이터의 클래스 불균형을 보정하였습니다.")
        except Exception as e:
            logging.error(f"SMOTE 적용 중 오류 발생: {e}")
            # SMOTE 실패시 원본 데이터를 사용하도록 함
            pass

    # (옵션 2) 클래스 가중치 조정: 원래 학습 데이터의 클래스 비율을 기반으로 가중치를 산출합니다.
    hyperparameters = {}
    if task == 'binary':
        counts = train_df[target].value_counts()
        if len(counts) == 2:
            majority_class = counts.idxmax()
            minority_class = counts.idxmin()
            # LightGBM과 XGBoost에서 scale_pos_weight는 다수 클래스 대비 소수 클래스의 비율
            scale_pos_weight = counts[majority_class] / counts[minority_class]
            print(f"계산된 scale_pos_weight: {scale_pos_weight:.2f}")

            hyperparameters = {
                'GBM': {'scale_pos_weight': scale_pos_weight},
                'XGB': {'scale_pos_weight': scale_pos_weight},
                # 필요 시 CatBoost 등 다른 모델도 설정 가능
            }
        else:
            print("이진 분류가 아닌 경우 클래스 가중치 조정은 생략합니다.")
    
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Bayesian Optimization을 사용하기 위한 설정
    hyperparameter_tune_kwargs = {
        'num_trials': 10,        # 시도 횟수 (증가 시 탐색 범위가 넓어지지만, 시간도 오래 걸림)
        'scheduler': 'local',    # 단일 머신에서 수행
        'searcher': 'auto',  # Bayesian Optimization 적용
    }
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    # 모델 학습
    predictor = TabularPredictor(
        label=target,
        problem_type=task,
        verbosity=2   # 튜닝 과정 자세히 보기 위해 verbosity=2 권장 (디폴트는 1)
    ).fit(
        train_data=train_df,
        time_limit=time_to_train,          
        presets=preset_str,  # 정수 대신 변환된 preset 문자열 사용
        hyperparameters=hyperparameters,
        hyperparameter_tune_kwargs=hyperparameter_tune_kwargs  # Bayesian Optimization 적용
    )

    y_pred = predictor.predict(test_df.drop(columns=[target]))  

    if task == 'regression':
        mae = mean_absolute_error(test_df[target], y_pred)
        r2 = r2_score(test_df[target], y_pred)
        print("AutoGluon Regressor 결과:")
        print(f" - MAE : {mae:.4f}")
        print(f" - R^2 : {r2:.4f}")
    elif task in ['binary', 'multiclass']:
        accuracy = accuracy_score(test_df[target], y_pred)
        f1 = f1_score(test_df[target], y_pred, average='weighted')
        print("AutoGluon Classifier 결과:")
        print(f" - Accuracy : {accuracy:.4f}")
        print(f" - F1 Score : {f1:.4f}")
    else:
        raise ValueError(f"Unsupported task type: {task}")

    leaderboard = predictor.leaderboard(test_df, silent=True)
    print(f'LeaderBoard Result :\n{leaderboard}')

    feature_importance = predictor.feature_importance(test_df)
    print(f'Feature Importance:\n{feature_importance}')
    print('==============================================================\n')
    print('==============================================================\n')

    evaluation = predictor.evaluate(test_df)
    print(f'Evaluation Results:\n{evaluation}')
    print('==============================================================\n')
    print('==============================================================\n')
    return predictor, test_df


def train_model(data, config):
    """
    auto_ml을 실행시킵니다.
    
    Args:
        data (pd.DataFrame): 전처리된 데이터셋
        config (dict): 설정값을 포함한 config 파일. 여기에는 task, target_feature, model_quality, time_to_train 등이 포함됨.
    
    Returns:
        model(Object): 학습된 모델
        test_df(pd.DataFrame): test에 사용된 데이터셋
    """
    model_config = config['model']
    task = model_config['task']
    target = config['target_feature']
    selected_quality = model_config['model_quality']
    time_to_train = model_config['time_to_train']
    try:
        model, test_df = automl_module(data, task, target, selected_quality, time_to_train)
        print('AutoGLuon에서 기대하는 클래스\n\n\n\n')
        print(model.class_labels)
        print('\n\n==========================================\n')
    except Exception as e:
        logging.error(f"Model training failed: {e}")
        return

    return model, test_df