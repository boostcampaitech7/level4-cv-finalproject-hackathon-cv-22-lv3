import optuna
import pandas as pd
from autogluon.tabular import TabularPredictor
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# def optimizeing_features(
#     predictor: TabularPredictor,
#     original_features: pd.Series,
#     feature_bounds: dict,
#     categorical_features: list,
#     task: str,
#     direction: str,
#     n_trials: int = 100,
#     target_class: str = None
# ):
#     """
#     특정 샘플의 피처를 변경하여 타겟 값을 최대화 또는 최소화하는 최적화 함수.
    
#     Parameters:
#         predictor (TabularPredictor): 학습된 AutoGluon 모델
#         original_features (pd.Series): 원본 피처 값
#         feature_bounds (dict): 변경 가능한 피처와 그 범위 {feature: (min, max)}
#         categorical_features (list): 카테고리형 피처 리스트
#         task (str): 문제 유형, 'regression', 'binary', 또는 'multiclass'
#         direction (str): 최적화 방향, 'maximize' 또는 'minimize'
#         n_trials (int): Optuna 최적화 반복 횟수
#         target_class (str, optional): 분류 문제에서 최적화할 클래스. 
#                                       None일 경우, 바이너리 분류는 긍정 클래스, 
#                                       멀티클래스 분류는 마지막 클래스를 사용.
    
#     Returns:
#         dict: 최적화된 피처 값
#         float: 최적화된 타겟 예측 값 (회귀의 경우 예측값, 분류의 경우 클래스 확률)
#     """
#     if direction not in ['maximize', 'minimize']:
#         raise ValueError("Direction must be either 'maximize' or 'minimize'")
    
#     if task not in ['regression', 'binary', 'multiclass']:
#         raise ValueError("Task must be one of 'regression', 'binary', or 'multiclass'")
    
#     def objective(trial):
#         modified_features = original_features.copy()
        
#         for feature, (low, high) in feature_bounds.items():
#             if feature in categorical_features:
#                 modified_features[feature] = trial.suggest_int(feature, low, high)
#             else:
#                 modified_features[feature] = trial.suggest_uniform(feature, low, high)
        
#         modified_df = pd.DataFrame([modified_features.to_dict()])
        
#         if task in ['binary', 'multiclass']:
#             proba = predictor.predict_proba(modified_df)
#             # 외부 target_class 값을 복사
#             local_target_class = target_class  
#             print(f'local_target_class: {local_target_class}')
#             print(f'predictor.class_labels: {predictor.class_labels}')
#             if task == 'binary':
#                 if local_target_class is None:
#                     target_class_proba = proba.iloc[0, 1]
#                 else:
#                     if local_target_class not in predictor.class_labels:
#                         raise ValueError(f"target_class '{local_target_class}' not found in model's class labels.")
#                     target_class_proba = proba.iloc[0, predictor.class_labels.index(local_target_class)]
#             else:  # multiclass
#                 if local_target_class is None:
#                     local_target_class = predictor.class_labels[-1]
#                 if local_target_class not in predictor.class_labels:
#                     raise ValueError(f"target_class '{local_target_class}' not found in model's class labels.")
#                 target_class_proba = proba.iloc[0, predictor.class_labels.index(local_target_class)]
            
#             return target_class_proba 
        
#         elif task == 'regression':
#             prediction = predictor.predict(modified_df).iloc[0]
#             return prediction 

#     study = optuna.create_study(direction=direction)
#     study.optimize(objective, n_trials=n_trials)
    
#     best_trial = study.best_trial
#     best_features = original_features.copy()
    
#     for feature in feature_bounds.keys():
#         if feature in categorical_features:
#             best_features[feature] = int(best_trial.params[feature]) 
#         else:
#             best_features[feature] = best_trial.params[feature]
    
#     if task in ['binary', 'multiclass']:
#         if task == 'binary' and target_class is None:
#             target_class = predictor.class_labels[1]
#         elif task == 'multiclass' and target_class is None:
#             target_class = predictor.class_labels[-1]
        
#         if target_class not in predictor.class_labels:
#             raise ValueError(f"target_class '{target_class}' not found in model's class labels.")
        
#         best_prediction = best_trial.value if direction == 'maximize' else -best_trial.value
#         if direction == 'minimize':
#             best_prediction = best_prediction * -1
#     elif task == 'regression':
#         best_prediction = best_trial.value if direction == 'maximize' else -best_trial.value
#         if direction == 'minimize':
#             best_prediction = best_prediction * -1
    
#     return best_features.to_dict(), best_prediction





import optuna
import pandas as pd

def optimizeing_features(
    predictor,
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
        (dict, float, float):
            1) 최적화된 피처 값 (dict)
            2) 최적화된 타겟 예측 값 (float)
            3) 원본 대비 향상된 정도 (float) 
    """
    if direction not in ['maximize', 'minimize']:
        raise ValueError("Direction must be either 'maximize' or 'minimize'")
    
    if task not in ['regression', 'binary', 'multiclass']:
        raise ValueError("Task must be one of 'regression', 'binary', or 'multiclass'")
    
    # =============================
    # 1) 원본(original) 예측값 계산
    # =============================
    original_df = pd.DataFrame([original_features.to_dict()])  # 1 x n DataFrame
    if task in ['binary', 'multiclass']:
        proba = predictor.predict_proba(original_df)
        
        # 분류에서 사용될 실제 타겟 클래스 확인(기존 로직 그대로 사용)
        local_target_class = target_class
        if task == 'binary':
            # 바이너리 분류의 경우, target_class가 None이면 모델의 두 번째 라벨 사용(양성 클래스)
            if local_target_class is None:
                local_target_class = predictor.class_labels[1]
            elif local_target_class not in predictor.class_labels:
                raise ValueError(f"target_class '{local_target_class}' not found in model's class labels.")
        else:  # multiclass
            # 멀티클래스 분류의 경우, target_class가 None이면 마지막 라벨 사용
            if local_target_class is None:
                local_target_class = predictor.class_labels[-1]
            elif local_target_class not in predictor.class_labels:
                raise ValueError(f"target_class '{local_target_class}' not found in model's class labels.")
        
        # 원본 샘플의 해당 클래스 확률
        class_index = predictor.class_labels.index(local_target_class)
        original_prediction = proba.iloc[0, class_index]
    else:
        # 회귀의 경우, 원본 예측값
        original_prediction = predictor.predict(original_df).iloc[0]
    
    # ==================================
    # 2) Objective 함수(Optuna 최적화용)
    # ==================================
    def objective(trial):
        modified_features = original_features.copy()
        
        # 범위 내에서 trial 제안 값으로 피처 수정
        for feature, (low, high) in feature_bounds.items():
            if feature in categorical_features:
                # 카테고리형은 int 값 제안
                modified_features[feature] = trial.suggest_int(feature, low, high)
            else:
                # 수치형은 float 값 제안
                modified_features[feature] = trial.suggest_uniform(feature, low, high)
        
        # 예측에 사용할 형태로 변환
        modified_df = pd.DataFrame([modified_features.to_dict()])
        
        if task in ['binary', 'multiclass']:
            proba = predictor.predict_proba(modified_df)
            
            # target_class가 None인 경우 처리 (binary, multiclass에 따라)
            local_target_class = target_class
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

    # ===================================
    # 3) Optuna 스터디 생성 및 최적화 수행
    # ===================================
    study = optuna.create_study(direction=direction)
    study.optimize(objective, n_trials=n_trials)
    
    # 최적화 결과
    best_trial = study.best_trial
    
    # ===========================================
    # 4) 최적화된 피처(best_features) 구성
    # ===========================================
    best_features = original_features.copy()
    for feature in feature_bounds.keys():
        if feature in categorical_features:
            best_features[feature] = int(best_trial.params[feature]) 
        else:
            best_features[feature] = best_trial.params[feature]
    
    # ===========================================
    # 5) 최적화된 최종 예측값(best_prediction)
    #    + 원본과 비교해 얼마나 향상됐는지(improvement)
    # ===========================================
    best_prediction = best_trial.value  # study.best_value 로 써도 동일
    
    # 만약 direction에 따라 "최적화한 값"이 이미 최대/최소 처리되어 있으므로
    # 따로 -best_trial.value 로 뒤집어줄 필요가 없습니다.
    # (study.best_value가 direction='maximize'이면 최대값, 'minimize'이면 최소값)
    # 
    # 하지만 아래와 같이 쓰는 경우도 있으므로 필요에 따라 조정 가능
    # if direction == 'maximize':
    #     best_prediction = best_trial.value
    # else:  # 'minimize'
    #     best_prediction = best_trial.value

    if direction == 'maximize':
        improvement = best_prediction - original_prediction
    else:  # 'minimize'
        improvement = original_prediction - best_prediction
    
    return best_features.to_dict(), best_prediction,original_prediction,  improvement