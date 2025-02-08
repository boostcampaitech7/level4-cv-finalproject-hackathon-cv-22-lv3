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