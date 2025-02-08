def identify_categorical_features(filtered_data: dict):    
    
    categorical_features = []
    
    for column_name, column_info in filtered_data.items():
        # 해당 column_info가 dict이고, 그 안에 "type": "Categorical"이 있으면 추가
        if isinstance(column_info, dict) and column_info.get("type") == "Categorical" or column_info.get("type") == "Boolean":
            categorical_features.append(column_name)
    
    return categorical_features