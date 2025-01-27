import pandas as pd

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
            print('____해당 task는 binary classification 입니다.____')
            return 'binary'
        elif num_unique <= threshold:
            print('____해당 task는 multiclass 입니다.____')
            return 'multiclass'
        else:
            print('____해당 task는 Regression 입니다.____')
            return 'regression'
    else:
        num_unique = target_series.nunique()
        if num_unique == 2:
            print('____해당 task는 binary classification 입니다.____')
            return 'binary'
        elif num_unique > 2:
            print('____해당 task는 multiclass 입니다.____')
            return 'multiclass'
        else:
            raise ValueError(f"타겟 컬럼 '{target}'은(는) 고유 값이 하나뿐입니다.")


