from typing import List, Dict


def identify_categorical_features(filtered_data: Dict[str, dict]) -> List[str]:
    '''
    Summary:
        주어진 데이터에서 범주형(Categorical) 또는 불리언(Boolean) feature를 식별하는 함수.

    Args:
        filtered_data (dict): 컬럼명을 key로 하고, 해당 컬럼의 속성을 포함하는 dict를 value로 가지는 딕셔너리.

    Returns:
        List[str]: 범주형 또는 불리언 feature의 컬럼명을 담은 리스트.
    '''
    categorical_features = []
    
    if not isinstance(filtered_data, dict):
        raise TypeError("filtered_data must be a dictionary.")
    
    categorical_features = [
        column_name
        for column_name, column_info in filtered_data.items()
        if isinstance(column_info, dict) and column_info.get("type") in {"Categorical", "Boolean"}
    ]

    return categorical_features