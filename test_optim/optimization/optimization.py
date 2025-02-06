import optuna
import pandas as pd
from autogluon.tabular import TabularPredictor
import optuna.visualization.matplotlib as ovm
import matplotlib.pyplot as plt
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def optimizeing_features(
    predictor: TabularPredictor,
    original_features: pd.Series,
    feature_bounds: dict,
    categorical_features: list,
    task: str,
    direction: str,
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
    if direction not in ['maximize', 'minimize']:
        raise ValueError("Direction must be either 'maximize' or 'minimize'")
    
    if task not in ['regression', 'binary', 'multiclass']:
        raise ValueError("Task must be one of 'regression', 'binary', or 'multiclass'")
    
    def objective(trial):
        modified_features = original_features.copy()
        
        for feature, (low, high) in feature_bounds.items():
            if feature in categorical_features:
                modified_features[feature] = trial.suggest_int(feature, low, high)
            else:
                modified_features[feature] = trial.suggest_uniform(feature, low, high)
        
        modified_df = pd.DataFrame([modified_features.to_dict()])
        
        if task in ['binary', 'multiclass']:
            proba = predictor.predict_proba(modified_df)
            # 외부 target_class 값을 복사
            local_target_class = target_class  
            print(f'local_target_class: {local_target_class}')
            print(f'predictor.class_labels: {predictor.class_labels}')
            if task == 'binary':
                if local_target_class is None:
                    target_class_proba = proba.iloc[0, 1]
                else:
                    if local_target_class not in predictor.class_labels:
                        raise ValueError(f"target_class '{local_target_class}' not found in model's class labels.")
                    target_class_proba = proba.iloc[0, predictor.class_labels.index(local_target_class)]
            else:  # multiclass
                if local_target_class is None:
                    local_target_class = predictor.class_labels[-1]
                if local_target_class not in predictor.class_labels:
                    raise ValueError(f"target_class '{local_target_class}' not found in model's class labels.")
                target_class_proba = proba.iloc[0, predictor.class_labels.index(local_target_class)]
            
            return target_class_proba 
        
        elif task == 'regression':
            prediction = predictor.predict(modified_df).iloc[0]
            return prediction 

    study = optuna.create_study(direction=direction)
    study.optimize(objective, n_trials=n_trials)
    
    best_trial = study.best_trial
    best_features = original_features.copy()
    
    for feature in feature_bounds.keys():
        if feature in categorical_features:
            best_features[feature] = int(best_trial.params[feature]) 
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
        if direction == 'minimize':
            best_prediction = best_prediction * -1
    elif task == 'regression':
        best_prediction = best_trial.value if direction == 'maximize' else -best_trial.value
        if direction == 'minimize':
            best_prediction = best_prediction * -1

    return best_features.to_dict(), best_prediction