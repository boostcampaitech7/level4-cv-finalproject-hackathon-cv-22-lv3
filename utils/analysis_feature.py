import json

def identify_categorical_features(json_path):
    """
    주어진 JSON 파일에서 "type": "Categorical" 인 컬럼명만 추출하여 리스트로 반환한다.
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    categorical_features = []
    for column_name, column_info in data.items():
        # column_info가 dict 타입일 때만 .get()을 사용
        if isinstance(column_info, dict):
            if column_info.get("type") == "Categorical":
                categorical_features.append(column_name)
        else:
            # 만약 column_info가 문자열이라면 그 값이 "Categorical"인지 직접 확인
            if column_info == "Categorical":
                categorical_features.append(column_name)
    return categorical_features