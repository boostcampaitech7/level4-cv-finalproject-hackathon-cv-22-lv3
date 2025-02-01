import pandas as pd
from utils.analysis_feature import identify_categorical_features
import logging

def determine_problem_type(data, target, threshold=10):
    """해당 Task가 어떤 종류의 Task인지 구분합니다.

    Args:
        data (csv): 학습할 데이터를 받아옵니다
        target (string): 목표로 하는 Feature를 의미합니다.
        threshold (int, optional): threshold 보다 적은 고유 종류를 갖는다면 다중분류 문제로 분류합니다.. Defaults to 10.

    Raises:
        ValueError: target이 학습 데이터에 존재하지 않는 경우

    Returns:
        string: 해당 task의 종류
    """
    if target not in data.columns:
        print(f'column들 리스트 {data.columns}')
        raise ValueError(f"타겟 컬럼 '{target}'이 데이터에 존재하지 않습니다.")
    
    target_series = data[target]
    
    if pd.api.types.is_numeric_dtype(target_series):
        num_unique = target_series.nunique()
        if num_unique <= 2:
            print('\n=================해당 task는 binary classification 입니다.=================\n')
            return 'binary'
        elif num_unique <= threshold:
            print('\n=================해당 task는 multiclass 입니다.=================\n')
            return 'multiclass'
        else:
            print('\n================해당 task는 Regression 입니다.=================\n')
            return 'regression'
    else:
        num_unique = target_series.nunique()
        if num_unique == 2:
            print('\n=================해당 task는 binary classification 입니다.=================\n')
            return 'binary'
        elif num_unique > 2:
            print('\n=================해당 task는 multiclass 입니다.=================\n')
            return 'multiclass'
        else:
            raise ValueError(f"타겟 컬럼 '{target}'은(는) 고유 값이 하나뿐입니다.")




def auto_determine_fixed_features(data, target, threshold=0.01):
    """
    자동으로 고정할 피처를 결정합니다.
    
    Parameters:
    - data (DataFrame): 데이터셋
    - target (str): 타겟 변수
    - threshold (float): 상관관계 절대값 기준
    
    Returns:
    - fixed_features (list): 고정할 피처 리스트
    """
    fixed_features = []
    
    # 1. ID 피처 감지 (예: 피처 이름에 'id' 포함)
    id_features = [col for col in data.columns if 'id' in col.lower()]
    fixed_features.extend(id_features)
    
    # 2. 날짜/시간 피처 감지
    date_features = []
    for col in data.columns:
        if pd.api.types.is_datetime64_any_dtype(data[col]):
            date_features.append(col)
    fixed_features.extend(date_features)
    
    # # 3. 상수 피처 감지
    # constant_features = [col for col in data.columns if data[col].nunique() == 1]
    # fixed_features.extend(constant_features)
    
    # 4. 낮은 상관관계 피처 감지
    correlation = data.corr()[target].abs()
    low_corr_features = correlation[correlation < threshold].index.tolist()
    fixed_features.extend(low_corr_features)
    
    # 중복 제거
    fixed_features = list(set(fixed_features))
    
    return fixed_features


def categorical_feature(data, threshold=10):    
    try:
        categorical_features = identify_categorical_features(data, threshold=10)
        logging.info(f"Identified categorical features: {categorical_features}")
    except Exception as e:
        logging.error(f"Failed to identify categorical features: {e}")
        return
    return categorical_features