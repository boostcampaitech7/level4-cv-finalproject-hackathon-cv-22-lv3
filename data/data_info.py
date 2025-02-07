import json
import logging
import pandas as pd
import os.path as osp
from omegaconf import OmegaConf
from ydata_profiling import ProfileReport

def generate_model_config(config_path):
    """
    summary: 모델 학습을 위한 model_config.json 생성 및 config.json 업데이트

    args:
        config (dict): 설정 정보를 담은 딕셔너리 (여기서 user_name, user_email 키 사용)
        data (pd.DataFrame): 분석할 데이터
        save_path (str): JSON 및 HTML 파일을 저장할 디렉터리 경로

    return:
        tuple: (json_file_path, eda_html_path) 저장된 JSON 및 HTML 파일 경로
    """
    # 기존 config 로드
    config = OmegaConf.load(config_path)

    user_name = config["user_name"]
    data_path = config["data_path"]
    save_path = osp.dirname(config_path)
    
    try:
        data = pd.read_csv(data_path)
        logging.info(f"Data loaded from {data_path}")
    except Exception as e:
        logging.error(f"Failed to load data: {e}")
        return

    # 저장 경로 설정
    json_filename = f"{user_name}_model_config.json"
    eda_html_filename = f"{user_name}_EDA_analysis.html"
    json_file_path = osp.join(save_path, json_filename)
    eda_html_path = osp.join(save_path, eda_html_filename)

    # ydata_profiling을 사용해 EDA 진행 후 HTML 저장
    profile = ProfileReport(data, explorative=True)
    profile.to_file(eda_html_path)

    # json 문자열을 dict 변환 후 OmegaConf 객체 생성
    original_eda_str = profile.to_json()
    original_eda_dict = json.loads(original_eda_str)
    original_eda = OmegaConf.create(original_eda_dict)
    
    # EDA 결과 필터링
    filtered_data = _extract_filtered_eda(original_eda)

    # 기존 config.json을 업데이트 (웹과 통신)
    updated_config = OmegaConf.merge(config, OmegaConf.create({
        "model_config_path": json_file_path,
        "eda_html_path": eda_html_path
    }))

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(OmegaConf.to_container(updated_config, resolve=True), f, indent=4, ensure_ascii=False)
    
    # model_config.json 생성 (서버 내부용)
    model_config = OmegaConf.merge(config, OmegaConf.create({
        "filtered_data": filtered_data,
    }))

    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(OmegaConf.to_container(model_config, resolve=True), f, indent=4, ensure_ascii=False)

    logging.info(f"웹과 통신할 config.json 저장 완료: {config_path}")
    logging.info(f"서버 내부용 model_config.json 저장 완료: {json_file_path}")
    logging.info(f"HTML 저장 완료: {eda_html_path}")

    return json_file_path

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
            'chi_squared': info.get('chi_squared', None),
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
    config_path = '/data/ephemeral/home/uploads/config.json'
    generate_model_config(config_path)