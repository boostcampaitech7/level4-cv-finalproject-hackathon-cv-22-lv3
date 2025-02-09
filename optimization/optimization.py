import optuna
import pandas as pd
from autogluon.tabular import TabularPredictor
import logging

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
    
    Returns:
        best_features (dict): 최적화된 피처 값
        best_prediction (float): 최적화된 타겟 예측 값
        original_prediction (float): 원본 샘플 예측 값
        improvement (float): 원본 대비 향상된 정도
    """
    import pandas as pd
    import optuna

    if direction not in ['maximize', 'minimize']:
        raise ValueError("Direction must be either 'maximize' or 'minimize'")
    
    if task not in ['regression', 'binary', 'multiclass']:
        raise ValueError("Task must be one of 'regression', 'binary', or 'multiclass'")
    
    # 1) 원본 예측값 계산
    original_df = pd.DataFrame([original_features.to_dict()])
    if task in ['binary', 'multiclass']:
        proba = predictor.predict_proba(original_df)
        
        local_target_class = target_class
        if task == 'binary':
            if local_target_class is None:
                local_target_class = predictor.class_labels[1]  # 양성 클래스
        else:  # multiclass
            if local_target_class is None:
                local_target_class = predictor.class_labels[-1]  # 마지막 클래스

        if local_target_class not in predictor.class_labels:
            raise ValueError(f"target_class '{local_target_class}' not found in model's class labels.")

        class_index = predictor.class_labels.index(local_target_class)
        original_prediction = proba.iloc[0, class_index]
    else:
        original_prediction = predictor.predict(original_df).iloc[0]
    
    # 2) Objective 함수 (Optuna 최적화용)
    def objective(trial):
        modified_features = original_features.copy()
        for feature, (low, high) in feature_bounds.items():
            if feature in categorical_features:
                # 카테고리형: 정수 범위 사용
                modified_features[feature] = trial.suggest_int(feature, low, high)
            else:
                # 숫자형: low와 high가 같으면 현재 값의 ± 퍼센트 범위로 자동 지정
                if low == high:
                    current_value = original_features[feature]
                    bound1 = current_value * (1 - low/100.0)
                    bound2 = current_value * (1 + high/100.0)
                    low_bound = min(bound1, bound2)
                    high_bound = max(bound1, bound2)
                    print(f'현재 값 = {current_value}')
                    print(f'{low_bound} ~ {high_bound} 까지의 값을 갖게 됩니다.')
                else:
                    if low > high:
                        tmp = low
                        low = high
                        high = tmp
                    low_bound, high_bound = low, high
                    
                modified_features[feature] = trial.suggest_uniform(feature, low_bound, high_bound)
        
        modified_df = pd.DataFrame([modified_features.to_dict()])
        
        if task in ['binary', 'multiclass']:
            proba = predictor.predict_proba(modified_df)
            local_tc = target_class
            if task == 'binary':
                if local_tc is None:
                    local_tc = predictor.class_labels[1]
            else:
                if local_tc is None:
                    local_tc = predictor.class_labels[-1]
            class_index_ = predictor.class_labels.index(local_tc)
            return proba.iloc[0, class_index_]
        else:
            return predictor.predict(modified_df).iloc[0]

    study = optuna.create_study(direction=direction)
    study.optimize(objective, n_trials=n_trials)
    
    # 3) 최적화 결과 추출
    best_trial = study.best_trial
    best_features = original_features.copy()
    for feature in feature_bounds.keys():
        if feature in categorical_features:
            best_features[feature] = int(best_trial.params[feature])
        else:
            best_features[feature] = best_trial.params[feature]

    best_prediction = best_trial.value 

    # 4) 향상도 계산
    if direction == 'maximize':
        improvement = best_prediction - original_prediction
    else:  # 'minimize'
        improvement = original_prediction - best_prediction
    
    return best_features.to_dict(), best_prediction, original_prediction, improvement