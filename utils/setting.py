import logging
import pandas as pd
import os
import json


def data_setting(config):
    """
    데이터를 불러오고, 모델 학습 및 최적화에 필요한 설정 값들을 추출하는 함수입니다.

    Args:
        config (dict): 설정 정보를 담고 있는 딕셔너리.

    Returns:
        data (pd.DataFrame): 불러온 데이터
        target (str): 타깃 변수 이름
        fixed_feature (list): 최적화에서 제외될 피처 목록
        selected_quality (str): 선택된 모델 품질 옵션
        time_to_train (int): 모델 학습 시간(초) 제한
        n_trials (int): 최적화 시도 횟수
    """
    data_path = config.get('data_path')
    target = config.get('target')

    try:
        data = pd.read_csv(data_path)
        logging.info(f"Data loaded from {data_path}")
    except Exception as e:
        logging.error(f"Failed to load data: {e}")
        return

    user_fixed_features = config.get('user_fixed_features', [])
    fixed_features = list(set(user_fixed_features))
    logging.info("============================================")
    logging.info("| Fixed Features (Not to be optimized) ")
    logging.info(f"| {fixed_features} ")
    logging.info("============================================\n\n")

    quality_map = config.get('quality_map')
    # JSON 파일에서 quality_map의 키가 문자열일 수 있으므로, 선택한 키를 문자열로 변환
    selected_quality = quality_map.get(str(config.get('selected_quality', 0)), "Invalid selection")
    if selected_quality == "Invalid selection":
        logging.error("Invalid quality selection. Please choose a valid option from quality_map.")
        return
    logging.info("============================================")
    logging.info("| quality")
    logging.info(f"| {selected_quality}")
    logging.info("============================================\n\n")

    time_to_train = config.get('time_to_train', 500)
    n_trials = config.get('n_trials', 100)

    return data, target, fixed_features, selected_quality, time_to_train, n_trials



def visualization_feature(data_path):
    """
    summary: JSON 파일에서 Feature 목록을 추출하여 시각화합니다.

    args:
        json_file_path (str): JSON 파일 경로
    
    return:
        None (시각화 결과 출력)
    """

    # JSON 파일 로드
    if not os.path.exists(data_path):
        print(f"파일을 찾을 수 없습니다: {data_path}")
        return

    with open(data_path, 'r', encoding='utf-8') as f:
        eda_data = json.load(f)

    features = list(eda_data.get('variables', {}).keys())
    return features