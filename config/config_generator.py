import json
import logging
from utils.logger_config import logger
import pandas as pd
import os.path as osp
from datetime import datetime, timezone, timedelta
from omegaconf import OmegaConf
from ydata_profiling import ProfileReport
from utils.analysis_feature import identify_categorical_features

def generate_config(data_path):
    """
    summary: 모델 학습을 위한 model_config.json 생성 및 user_config.json 업데이트

    args:
        config (dict): 설정 정보를 담은 딕셔너리 (여기서 user_name, user_email 키 사용)
        data (pd.DataFrame): 분석할 데이터
        save_path (str): JSON 및 HTML 파일을 저장할 디렉터리 경로

    return:
        tuple: (json_file_path, eda_html_path) 저장된 JSON 및 HTML 파일 경로
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

    # 저장 경로 설정
    user_config_filename = f'{timestamp}_user_config.json'
    model_config_filename = f"model_config.json"
    eda_html_filename = f"EDA_analysis.html"
    
    user_config_path = osp.join(save_path, user_config_filename)
    model_config_path = osp.join(save_path, model_config_filename)
    eda_html_path = osp.join(save_path, eda_html_filename)

    # 고유값이 하나일 경우 drop
    for col in data.columns:
        if len(data[col].unique()) == 1:
            data.drop(columns=[col], inplace=True)

    # ydata_profiling을 사용해 EDA 진행 후 HTML 저장
    profile = ProfileReport(data, explorative=True)
    profile.to_file(eda_html_path)

    # json 문자열을 dict 변환 후 OmegaConf 객체 생성
    original_eda_str = profile.to_json()
    original_eda_dict = json.loads(original_eda_str)
    original_eda = OmegaConf.create(original_eda_dict)
    
    # EDA 결과 필터링
    filtered_data = _extract_filtered_eda(original_eda)
    correlations = original_eda.get("correlations")
    categorical_feature = identify_categorical_features(filtered_data)

    # config 객체 생성
    config = OmegaConf.create({})

    # 기존 config.json을 업데이트 (웹과 통신)
    user_config = OmegaConf.merge(config, OmegaConf.create({
        "model_config_path": model_config_path,
        "eda_html_path": eda_html_path,
        "features" : list(data.columns)
    }))

    with open(user_config_path, 'w', encoding='utf-8') as f:
        json.dump(OmegaConf.to_container(user_config, resolve=True), f, indent=4, ensure_ascii=False)
    
    # model_config.json 생성 (서버 내부용)
    model_config = OmegaConf.merge(config, OmegaConf.create({
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
        "feature_importance" : {},
    }))

    with open(model_config_path, 'w', encoding='utf-8') as f:
        json.dump(OmegaConf.to_container(model_config, resolve=True), f, indent=4, ensure_ascii=False)

    logger.info(f"웹과 통신할 config.json 저장 완료: {user_config_path}")
    logger.info(f"서버 내부용 model_config.json 저장 완료: {model_config_path}")
    logger.info(f"HTML 저장 완료: {eda_html_path}")

    return model_config_path, user_config_path, data


def _extract_filtered_eda(config):
    """
    summury: EDA 결과에서 필요한 데이터만 필터링
    
    Args:
    
    Returns:
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

if __name__ == "__main__":
    data_path = '/data/ephemeral/home/uploads/WA_Fn-UseC_-HR-Employee-Attrition.csv'
    model_config_path, user_config_path, original_df = generate_config(data_path)
