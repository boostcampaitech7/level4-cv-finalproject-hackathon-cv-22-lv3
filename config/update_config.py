import os.path as osp
import json
from utils.logger_config import logger
from datetime import datetime
from omegaconf import OmegaConf

import numpy as np

def convert_numpy_types(data):
    if isinstance(data, dict):
        return {k: convert_numpy_types(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_numpy_types(item) for item in data]
    elif isinstance(data, np.generic):
        return data.item()  # NumPy scalar를 Python 기본형으로 변환
    else:
        return data
        

def update_config(config_path, config_updates):
    '''
    '''
    try:
        config = OmegaConf.load(config_path)
        logger.info(f"설정 파일 로드 완료 : {config_path}")
    except FileNotFoundError:
        logger.warning(f"파일을 찾을 수 없습니다.")
    
    config_updates = convert_numpy_types(config_updates)
    updated_config = OmegaConf.merge(config, OmegaConf.create(config_updates))

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(OmegaConf.to_container(updated_config, resolve=True), f, indent=4, ensure_ascii=False)
        
        logger.info(f"설정 파일 업데이트 완료 : {config_path}")

    return config_path

if __name__ == "__main__":
    config_path = '/data/ephemeral/home/uploads/model_config.json'
    config_updates = {
        "target_feature": "test",
        "controllabel_feature": "test",
        "necessary_feature": "test",
        "limited_feature" : "test",
        }
    
    update_config = update_config(config_path, config_updates)