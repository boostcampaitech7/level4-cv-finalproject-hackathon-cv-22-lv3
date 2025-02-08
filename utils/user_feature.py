import pandas as pd
import numpy as np
from omegaconf import OmegaConf

def user_feature(data, model_config_path):
    '''
    process_2 단계에서 필요한 정보를 웹에 전달합니다.
    제어 변수, 타겟 변수의 범위 및 feature 정보를 추출
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
    # EDA를 통하 feature 정보
    filtered_data = config["filtered_data"]
    # task
    task = config["task"]
    # 상관 계수 결과
    correlations_result = config["correlations_result"]
    # 제어변수
    controllable_feature = config["controllable_feature"]
    # 타겟변수
    target_feature = config["target_feature"]
    # 모델 학습 결과
    model_result = config["model_result"]
    # 모델 리더보드
    top_models = config["Top_models"]
    # 피처 중요도
    feature_importance = config["feature_importance"]

    # task
    update_config["task"] = task
    
    # 상관 계수
    update_config["correlations_result"] = correlations_result

    # 제어변수 범위 섫정
    if len(controllable_feature) == 1:
        info = extract_feature_range(data, filtered_data, controllable_feature)
        update_config["controllable_range"][controllable_feature] = info
    else:
        for col in controllable_feature:
            info = extract_feature_range(data, filtered_data, col)
            update_config["controllable_range"][col] = info
    
    # 타겟변수 범위 섫정
    if target_feature:
        info = extract_feature_range(data, filtered_data, target_feature)
        update_config["target_range"][target_feature] = info

    # 학습 결과
    update_config["model_result"] = model_result

    # 모델 리더보드
    update_config["top_models"] = top_models
    
    # 피처 중요도
    update_config["feature_importance"] = feature_importance


    return update_config


def extract_feature_range(data, filtered_data, feature):
    """ 
    주어진 feature의 값을 기반으로 범위를 추출하는 함수.

    Args:
        data (pd.DataFrame): 원본 데이터
        filtered_data (dict): 필터링된 데이터 정보 (EDA 결과)
        feature (str): 처리할 feature 이름

    Returns:
        list: [범위 정보, 데이터 타입]
    """
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


if __name__ in "__main__":
    df = pd.read_csv("/data/ephemeral/home/uploads/WA_Fn-UseC_-HR-Employee-Attrition.csv")
    model_config_path = '/data/ephemeral/home/uploads/model_config.json'

    update_config = user_feature(df, model_config_path)
    print(update_config)