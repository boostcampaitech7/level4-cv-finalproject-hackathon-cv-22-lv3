import json
from omegaconf import OmegaConf
from utils.logger_config import logger

import numpy as np
# 이 함수 Utils로 옮기기
def convert_numpy_types(data):
    '''
    Summary: 
        Numpy 자료형을 Python 기본 자료형으로 변환하는 재귀 함수.

    Args: 
        data (dict, list, np.generic, any): 변환할 데이터.

    Returns: 
        변환된 데이터 (dict, list, int, float, any).
    '''
    if isinstance(data, dict):
        return {k: convert_numpy_types(v) for k, v in data.items()}    
    elif isinstance(data, list):
        return [convert_numpy_types(item) for item in data]

    elif isinstance(data, np.generic):
        return data.item()
    else:
        return data

def update_config(config_path: str, config_updates: dict) -> str:
    '''
    Summary: 
        기존 설정 파일을 업데이트하고 저장하는 함수

    Args:
        config_path (str): 업데이트할 설정 파일(.json)의 경로
        config_updates (dict): 설정 파일에 추가하거나 변경할 값이 포함된 딕셔너리
    
    Returns: 
        config_path (str): 업데이트된 설정 파일의 경로 
    '''
    try:
        config = OmegaConf.load(config_path)
        logger.info(f"Configuration file loaded successfully: {config_path}")
    except FileNotFoundError:
        logger.warning("Configuration file not found.")    
    
    config_updates = convert_numpy_types(config_updates)
    updated_config = OmegaConf.merge(config, OmegaConf.create(config_updates))

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(OmegaConf.to_container(updated_config, resolve=True), f, indent=4, ensure_ascii=False)
        
        logger.info(f"Configuration file updated successfully: {config_path}")

    return config_path