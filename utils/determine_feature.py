import pandas as pd
from omegaconf import OmegaConf
from config.update_config import update_config
from utils.logger_config import logger


def determine_problem_type(config_path: str, threshold: int = 10) -> str:
    """
    Summary:
        데이터의 target 값을 기반으로 해당 Task 유형을 결정합니다.

    Args:
        config_path (str): 설정 파일(.json)의 경로.
        threshold (int, optional): threshold보다 적은 고유값을 가지면 다중분류(multiclass)로 설정. 기본값은 10.

    Returns:
        str: 결정된 Task 유형 ('binary', 'multiclass', 'regression').
    """
    config = OmegaConf.load(config_path)
    
    target = config["target_feature"]
    data = pd.read_csv(config["data_path"])
    
    if target not in data.columns:
        raise ValueError(f"타겟 컬럼 '{target}'이 데이터에 존재하지 않습니다.")
    
    target_series = data[target]
    num_unique = target_series.nunique()

    if num_unique == 1:
        raise ValueError(f"타겟 컬럼 '{target}'은(는) 고유 값이 하나뿐입니다.")

    if pd.api.types.is_numeric_dtype(target_series):
        if num_unique <= 2:
            task = "binary"
        elif num_unique <= threshold:
            task = "multiclass"
        else:
            task = "regression"
    else:
        task = "binary" if num_unique == 2 else "multiclass"
    
    logger.info(f"task 설정: {task}")
    update_config(config_path, {"task": task})

    return task