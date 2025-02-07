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



import os
import json

def visualization_feature(json_file_path):
    """
    summary: 
      - JSON 파일(예: ydata_profiling 결과)을 읽어서,
        1) 전체 feature 목록
        2) character_counts에서 '첫 번째 키가 숫자'이거나, 
           character_counts가 아예 없는 feature 목록
      을 추출해 반환합니다.

    args:
        json_file_path (str): JSON 파일 경로 (예: ydata_profiling으로 생성된 config JSON)

    returns:
        tuple(list, list):
            - (1) 전체 feature 이름 리스트
            - (2) 조건에 맞는(numeric_key_features) feature 이름 리스트
    """

    if not os.path.exists(json_file_path):
        print(f"파일을 찾을 수 없습니다: {json_file_path}")
        return [], []

    with open(json_file_path, 'r', encoding='utf-8') as f:
        eda_data = json.load(f)

    # 'variables' 키에 대한 기본값은 빈 dict로 설정
    variables = eda_data.get('variables', {})

    # 전체 feature 목록
    all_features = list(variables.keys())

    # 첫 번째 key가 '숫자'인 경우 or char_counts가 아예 없는 경우
    numeric_key_features = []

    for feature_name, feature_info in variables.items():
        # character_counts 추출
        char_counts = feature_info.get('character_counts', {})

        if len(char_counts) == 0:
            # character_counts가 비어있으면 포함
            numeric_key_features.append(feature_name)
        else:
            # 첫 번째 key 확인
            first_key = list(char_counts.keys())[0]
            # 문자열이 '숫자' 형태인지 확인: str.isdigit()
            if first_key.isdigit():
                numeric_key_features.append(feature_name)
            # else: 첫 번째 key가 숫자가 아니므로 제외

    return all_features, numeric_key_features