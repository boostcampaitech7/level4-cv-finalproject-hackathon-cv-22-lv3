import pandas as pd
import numpy as np
from omegaconf import OmegaConf


def update_user_feature(data: pd.DataFrame, model_config_path: str) -> dict:
    '''
    Summary:
        모델 학습 과정에서 생성된 feature 정보를 바탕으로 user_config에 저장할 딕셔너리를 생성하는 함수.
        제어 변수(Controllable Features)와 타겟 변수(Target Feature)의 값 범위를 계산하여 포함.
        모델 학습 결과 및 상관 계수 분석 결과를 포함하여 user_config 저장에 필요한 데이터를 구성.

    Args:
        data (pd.DataFrame): 원본 데이터.
        model_config_path (str): 모델 설정 파일의 경로.

    Returns:
        dict: user_config 갱신에 필요한 feature 정보 및 모델 학습 결과가 포함된 딕셔너리.
    '''
    update_config = {
        "task" : None,
        "correlations_result" : None,
        "controllable_range" : {},
        "target_range" : {},
        "model_result" : None,
        "top_models" : None,
        "feature_importance": None
    }

    config = OmegaConf.load(model_config_path)
    
    filtered_data = config["filtered_data"]
    task = config["task"]
    correlations_result = config["correlations_result"]
    controllable_feature = config["controllable_feature"]
    target_feature = config["target_feature"]
    model_result = config["model_result"]
    top_models = config["top_models"]
    feature_importance = config["feature_importance"]

    update_config["task"] = task
    update_config["correlations_result"] = correlations_result

    if len(controllable_feature) == 1:
        info = extract_feature_range(data, filtered_data, controllable_feature)
        update_config["controllable_range"][controllable_feature] = info
    else:
        for col in controllable_feature:
            info = extract_feature_range(data, filtered_data, col)
            update_config["controllable_range"][col] = info
    
    if target_feature:
        info = extract_feature_range(data, filtered_data, target_feature)
        update_config["target_range"][target_feature] = info

    update_config["model_result"] = model_result
    update_config["top_models"] = top_models
    update_config["feature_importance"] = feature_importance

    return update_config


def extract_feature_range(data, filtered_data, feature):
    ''' 
    Summary:
        주어진 feature의 값을 기반으로 범위를 추출하는 함수.

    Args:
        data (pd.DataFrame): 원본 데이터.
        filtered_data (dict): 필터링된 데이터 정보 (EDA 결과).
        feature (str): 처리할 feature 이름.

    Returns:
        list: [범위 정보, 데이터 타입]
    '''
    col_type = filtered_data[feature].get("type", None)

    if col_type in ["Categorical", "Boolean"]:
        if not np.issubdtype(data[feature].dtype, np.integer):
            str_range = sorted(data[feature].unique())
            int_range = list(range(len(str_range)))
            return [str_range, int_range, col_type, "str"]
        else:
            int_range = sorted(map(int, data[feature].unique()))
            return [int_range, col_type, "int"]

    elif col_type == "Numeric":
        min_val = filtered_data[feature].get("min", data[feature].min())
        max_val = filtered_data[feature].get("max", data[feature].max())
        int_range = [min_val, max_val]
        return [int_range, "Numeric"]

    return None