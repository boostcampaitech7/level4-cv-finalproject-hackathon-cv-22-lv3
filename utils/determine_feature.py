import logging
from omegaconf import OmegaConf
import pandas as pd
from config.update_config import update_config

def determine_problem_type(config_path, threshold=10):
    """해당 Task가 어떤 종류의 Task인지 구분합니다.

    Args:
        data (csv): 학습할 데이터를 받아옵니다.
        target (string): 목표로 하는 Feature를 의미합니다.
        threshold (int, optional): threshold 보다 적은 고유 종류를 갖는다면 다중분류 문제로 분류합니다. Defaults to 10.

    Raises:
        ValueError: target이 학습 데이터에 존재하지 않는 경우

    Returns:
        string: 해당 task의 종류
    """
    config = OmegaConf.load(config_path)
    
    target = config["target_feature"]
    data = pd.read_csv(config["data_path"])
    
    if target not in data.columns:
        #print(f'column들 리스트 {data.columns}')
        raise ValueError(f"타겟 컬럼 '{target}'이 데이터에 존재하지 않습니다.")
    
    target_series = data[target]
    
    if pd.api.types.is_numeric_dtype(target_series):
        num_unique = target_series.nunique()
        if num_unique <= 2:
            #print('\n=================해당 task는 binary classification 입니다.=================\n')
            logging.info("task 설정 : binary classification")
            config_updates = {"task": 'binary'}
            update_config(config_path, config_updates)
        elif num_unique <= threshold:
            #print('\n=================해당 task는 multiclass 입니다.=================\n')
            logging.info("task 설정 : multiclass classification")
            config_updates = {"task": 'multiclass'}
            update_config(config_path, config_updates)
        else:
            #print('\n================해당 task는 Regression 입니다.=================\n')
            logging.info("task 설정 : regression")
            config_updates = {"task": 'regression'}
            update_config(config_path, config_updates)
    else:
        num_unique = target_series.nunique()
        if num_unique == 2:
            #print('\n=================해당 task는 binary classification 입니다.=================\n')
            logging.info("task 설정 : binary classification")
            config_updates = {"task": 'binary'}
            update_config(config_path, config_updates)
        elif num_unique > 2:
            #print('\n=================해당 task는 multiclass 입니다.=================\n')
            logging.info("task 설정 : multiclass classification")
            config_updates = {"task": 'multiclass'}
            update_config(config_path, config_updates)
        else:
            raise ValueError(f"타겟 컬럼 '{target}'은(는) 고유 값이 하나뿐입니다.")