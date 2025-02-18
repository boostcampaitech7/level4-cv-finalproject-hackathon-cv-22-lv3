import pandas as pd
from typing import Union, Dict, List


def compare_features(
    original_features: Union[pd.Series, Dict[str, Union[int, float, str]]],
    optimized_features: Union[pd.Series, Dict[str, Union[int, float, str]]],
    categorical_features: List[str]
) -> str:
    '''
    Summary:
        원본 피처와 최적화된 피처를 비교하여 출력하는 함수입니다.
        원본 값과 최적화된 값을 비교하여 DataFrame 형식으로 변환.
    
    Args:
        original_features (pd.Series or dict): 원본 Feature 이름과 값.
        optimized_features (pd.Series or dict): 최적화된 Feature 이름과 값.
        categorical_features (list): 카테고리형 Feature 목록.
    Returns:
        str: Feature 비교 결과를 문자열 형태로 반환.
    '''
    comparison_df = pd.DataFrame({
        'Feature': original_features.index,
        'Type': ['Categorical' if feat in categorical_features else 'Numerical' for feat in original_features.index],
        'Original': original_features.values,
        '->' : '->',
        'Optimized': optimized_features.values
    })
    
    return comparison_df.to_string(index=False)