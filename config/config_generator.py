import json
import os.path as osp
from datetime import datetime, timezone, timedelta
import pandas as pd
from omegaconf import OmegaConf
from ydata_profiling import ProfileReport
from utils.logger_config import logger
from utils.analysis_feature import identify_categorical_features
from typing import Tuple


def generate_config(data_path: str) -> Tuple[str, str, pd.DataFrame]:
    """
    Summary: 
        모델 학습을 위한 설정 파일(model_config.json, user_config.json) 생성 및 EDA 결과 저장.

    Args:
        data_path (str): 분석할 데이터 CSV 파일의 경로.
    
    Returns:
        model_config_path (str): 생성된 모델 설정 파일(model_config.json) 경로.
        user_config_path (str): 웹가 통신할 설정 파일(user_config.json) 경로.
        data (Pd.DataFrame): 로드된 원본 데이터.
    """
    save_path = osp.dirname(data_path)
    
    try:
        data = pd.read_csv(data_path)
        logger.info(f"Data loaded from {data_path}")
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        return

    kst = timezone(timedelta(hours=9))
    timestamp = datetime.now(kst).strftime("%Y%m%d_%H%M%S")

    user_config_filename = f'{timestamp}_user_config.json'
    model_config_filename = f"model_config.json"
    eda_html_filename = f"EDA_analysis.html"
    
    user_config_path = osp.join(save_path, user_config_filename)
    model_config_path = osp.join(save_path, model_config_filename)
    eda_html_path = osp.join(save_path, eda_html_filename)

    for col in data.columns:
        if len(data[col].unique()) == 1:
            data.drop(columns=[col], inplace=True)

    profile = ProfileReport(data, explorative=True)
    profile.to_file(eda_html_path)

    original_eda_str = profile.to_json()
    original_eda_dict = json.loads(original_eda_str)
    original_eda = OmegaConf.create(original_eda_dict)
    
    filtered_data = _extract_filtered_eda(original_eda)
    correlations = original_eda.get("correlations")
    categorical_feature = identify_categorical_features(filtered_data)

    config = OmegaConf.create({})

    user_config = OmegaConf.merge(
                    config, 
                    OmegaConf.create({
                            "model_config_path": model_config_path,
                            "eda_html_path": eda_html_path,
                            "features" : list(data.columns)
                            }))

    with open(user_config_path, 'w', encoding='utf-8') as f:
        json.dump(OmegaConf.to_container(user_config, resolve=True), f, indent=4, ensure_ascii=False)
    
    model_config = OmegaConf.merge(
                    config, 
                    OmegaConf.create({
                            "data_path": data_path,
                            "save_path": save_path,
                            "features": list(data.columns),
                            "filtered_data": filtered_data,
                            "correlations": correlations,
                            "correlations_result": None,
                            "final_features" : None,
                            "categorical_features" : categorical_feature,
                            "model_result" : {},
                            "top_models" : {},
                            "feature_importance" : {}
                            }))

    with open(model_config_path, 'w', encoding='utf-8') as f:
        json.dump(OmegaConf.to_container(model_config, resolve=True), f, indent=4, ensure_ascii=False)

    logger.info(f"Config.json for web communication saved: {user_config_path}")
    logger.info(f"Model_config.json for server use saved: {model_config_path}")
    logger.info(f"EDA HTML report saved: {eda_html_path}")

    return model_config_path, user_config_path, data


def _extract_filtered_eda(config: dict) -> dict:
    """
    Summary: 
        EDA 결과에서 필요한 통계 정보를 필터링하여 반환하는 함수.
    
    Args:
        config (dict): 변수별 통계 정보가 포함된 EDA 결과 딕셔너리.
    
    Returns:
        filtered_data (dict): 필터링된 통계 정보를 포함하는 딕셔너리.
    """
    filtered_data = {
        var_name: {
            'type': info.get('type', None),
            'p_missing': info.get('p_missing', None),
            'n_distinct': info.get('n_distinct', None),
            'p_distinct': info.get('p_distinct', None),
            'mean': info.get('mean', None),
            'std': info.get('std', None),
            'variance': info.get('variance', None),
            'min': info.get('min', None),
            'max': info.get('max', None),
            'kurtosis': info.get('kurtosis', None),
            'skewness': info.get('skewness', None),
            'mad': info.get('mad', None),
            'range': info.get('range', None),
            'iqr': info.get('iqr', None),
            'range': info.get('range', None),
            'Q1': info.get('25%', None),
            'Q3': info.get('75%', None)
        }
        for var_name, info in config.get('variables', {}).items()
    }
    
    return filtered_data