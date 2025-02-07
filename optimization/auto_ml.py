import pandas as pd
import logging
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score, f1_score
from autogluon.tabular import TabularPredictor


def automl_module(data, task, target, preset, time_to_train):
    """Autogluon 라이브러리를 활용하여 자동으로 모델을 실행시킵니다.

    Args:
        data (pd.DataFrame): 전처리된 데이터셋
        task (str): 수행할 task
        target (str): target feature
        preset (int): 모델의 정도 (0~3 정수값)
        time_to_train (int): 학습 시간 (초 단위)

    Raises:
        KeyError: target이 데이터셋에 존재하지 않는 경우 에러 발생
        ValueError: task type이 예상치 못한 답을 얻는 경우 에러 발생

    Returns:
        predictor(Object): 학습된 모델
        test_df(pd.DataFrame) : test에 사용된 데이터셋
    """ 
    # preset 정수를 문자열 preset으로 변환하는 매핑
    preset_mapping = {
        0: "best_quality",
        1: "high_quality",
        2: "good_quality",
        3: "medium_quality"
    }
    preset_str = preset_mapping.get(preset, "medium_quality")  # 기본값은 medium_quality

    # 데이터 분할
    if task == 'regression':
        train_df, test_df = train_test_split(data, test_size=0.2, random_state=42)
    else:
        train_df, test_df = train_test_split(data, test_size=0.2, random_state=42, stratify=data[target])
    
    if target not in train_df.columns:
        raise KeyError(f"Label column '{target}' is missing from training data. Training data columns: {list(train_df.columns)}")

    # 모델 학습
    predictor = TabularPredictor(
        label=target,             
        problem_type=task,
        verbosity=1
    ).fit(
        train_data=train_df, 
        time_limit=time_to_train,          
        presets=preset_str   # 정수 대신 변환된 preset 문자열 사용
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
    """auto_ml을 실행시킨다

    Args:
        data (pd.DataFrame): 전처리된 데이터셋
        task (str): 수행할 task
        target (str): 최적화 할 feature
        preset (int): 모델의 정도
        time_to_train (int): 학습 시간

    Returns:
        model(Object): 학습된 모델
        test_df(pd.DataFrame) : test에 사용된 데이터셋
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