import optuna
import pandas as pd
from autogluon.tabular import TabularPredictor
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def optimize_features(
    predictor: TabularPredictor,
    original_features: pd.Series,
    feature_bounds: dict,
    categorical_features: list,
    task: str,
    direction: str = 'maximize',
    n_trials: int = 100,
    target_class: str = None
):
    """
    특정 샘플의 피처를 변경하여 타겟 값을 최대화 또는 최소화하는 최적화 함수.
    
    Parameters:
        predictor (TabularPredictor): 학습된 AutoGluon 모델
        original_features (pd.Series): 원본 피처 값
        feature_bounds (dict): 변경 가능한 피처와 그 범위 {feature: (min, max)}
        categorical_features (list): 카테고리형 피처 리스트
        task (str): 문제 유형, 'regression', 'binary', 또는 'multiclass'
        direction (str): 최적화 방향, 'maximize' 또는 'minimize'
        n_trials (int): Optuna 최적화 반복 횟수
        target_class (str, optional): 분류 문제에서 최적화할 클래스. 
                                      None일 경우, 바이너리 분류는 긍정 클래스, 
                                      멀티클래스 분류는 마지막 클래스를 사용.
    
    Returns:
        dict: 최적화된 피처 값
        float: 최적화된 타겟 예측 값 (회귀의 경우 예측값, 분류의 경우 클래스 확률)
    """
    # 입력 검증
    if direction not in ['maximize', 'minimize']:
        raise ValueError("Direction must be either 'maximize' or 'minimize'")
    
    if task not in ['regression', 'binary', 'multiclass']:
        raise ValueError("Task must be one of 'regression', 'binary', or 'multiclass'")
    
    def objective(trial):
        modified_features = original_features.copy()
        
        for feature, (low, high) in feature_bounds.items():
            if feature in categorical_features:
                # 카테고리형 피처는 정수형 값을 사용
                modified_features[feature] = trial.suggest_int(feature, low, high)
            else:
                # 수치형 피처는 연속적인 값을 사용
                modified_features[feature] = trial.suggest_uniform(feature, low, high)
        
        # 예측값 계산
        modified_df = pd.DataFrame([modified_features.to_dict()])
        
        if task in ['binary', 'multiclass']:
            # 분류 문제에서는 클래스 확률을 사용
            proba = predictor.predict_proba(modified_df)
            if task == 'binary':
                # 바이너리 분류에서는 두 클래스의 확률이 반환됩니다.
                # target_class가 None이면 긍정 클래스(보통 1)를 사용
                if target_class is None:
                    target_class_proba = proba.iloc[0, 1]
                else:
                    if target_class not in predictor.class_labels:
                        raise ValueError(f"target_class '{target_class}' not found in model's class labels.")
                    target_class_proba = proba.iloc[0, predictor.class_labels.index(target_class)]
            else:
                # 멀티클래스 분류에서는 target_class를 지정해야 합니다.
                if target_class is None:
                    # 지정하지 않으면 마지막 클래스를 사용
                    target_class = predictor.class_labels[-1]
                if target_class not in predictor.class_labels:
                    raise ValueError(f"target_class '{target_class}' not found in model's class labels.")
                target_class_proba = proba.iloc[0, predictor.class_labels.index(target_class)]
            
            logger.debug(f"Modified Features: {modified_features.to_dict()}")
            logger.debug(f"Prediction Probabilities: {proba}")
            logger.debug(f"Target Class Probability ({target_class}): {target_class_proba}")
            
            # Optuna는 'maximize' 또는 'minimize' 방향을 사용하므로, 'minimize'일 때는 부호를 반전
            return target_class_proba if direction == 'maximize' else -target_class_proba
        
        elif task == 'regression':
            # 회귀 문제에서는 예측값 자체를 사용
            prediction = predictor.predict(modified_df).iloc[0]
            logger.debug(f"Modified Features: {modified_features.to_dict()}")
            logger.debug(f"Prediction: {prediction}")
            return prediction if direction == 'maximize' else -prediction

    # Optuna 스터디 생성 시 방향 설정
    study = optuna.create_study(direction=direction)
    study.optimize(objective, n_trials=n_trials)
    
    best_trial = study.best_trial
    best_features = original_features.copy()
    
    for feature in feature_bounds.keys():
        if feature in categorical_features:
            best_features[feature] = int(best_trial.params[feature])  # 정수형으로 변환
        else:
            best_features[feature] = best_trial.params[feature]
    
    if task in ['binary', 'multiclass']:
        if task == 'binary' and target_class is None:
            target_class = predictor.class_labels[1]
        elif task == 'multiclass' and target_class is None:
            target_class = predictor.class_labels[-1]
        
        if target_class not in predictor.class_labels:
            raise ValueError(f"target_class '{target_class}' not found in model's class labels.")
        
        best_prediction = best_trial.value if direction == 'maximize' else -best_trial.value
        # 'minimize'일 경우 확률을 원래대로 돌려놓음
        if direction == 'minimize':
            best_prediction = best_prediction * -1
    elif task == 'regression':
        best_prediction = best_trial.value if direction == 'maximize' else -best_trial.value
        if direction == 'minimize':
            best_prediction = best_prediction * -1
    
    return best_features.to_dict(), best_prediction