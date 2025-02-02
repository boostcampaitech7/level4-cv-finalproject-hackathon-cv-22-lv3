import json

def identify_categorical_features(json_path):
    """
    주어진 JSON 파일에서 "type": "Categorical" 인 컬럼명만 추출하여 리스트로 반환한다.
    (단, "filtered_result" 키 아래의 데이터만 확인)
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 최상위 JSON에서 "filtered_result" 부분만 추출
    filtered_data = data.get("filtered_result", {})
    
    categorical_features = []
    # filtered_result 딕셔너리를 순회
    for column_name, column_info in filtered_data.items():
        # 해당 column_info가 dict이고, 그 안에 "type": "Categorical"이 있으면 추가
        if isinstance(column_info, dict) and column_info.get("type") == "Categorical":
            categorical_features.append(column_name)
    
    return categorical_features



# import json

# def identify_categorical_features(data,threshold=10):
#     categorical_features = [col for col in data.columns if data[col].nunique() <= threshold]
#     # print('\n\n')
#     # print(f"\nCategorical Features Identified: {categorical_features}")
#     # print('\n\n')
#     return categorical_features
