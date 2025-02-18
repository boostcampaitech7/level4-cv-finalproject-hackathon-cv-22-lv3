from sklearn.metrics import r2_score
from typing import Union
import numpy as np
import pandas as pd


def adjusted_r2_score(y_true: Union[list, np.ndarray, pd.Series], 
                      y_pred: Union[list, np.ndarray, pd.Series],
                      n_features: Union[int, pd.DataFrame]) -> float:
    """
    Summary: 
        조정된 R² (Adjusted R²) 값을 계산하는 함수.
        R² 값을 기반으로 독립 변수 개수를 고려하여 조정된 R² 값을 반환.

    Args:
        y_true (array-like): 실제 값 (정답 레이블).
        y_pred (array-like): 예측 값.
        n_features (int or pd.DataFrame): 독립 변수의 개수 또는 독립 변수들을 포함하는 DataFrame.

    Returns:
        float: 조정된 R² 값
    """
    if hasattr(n_features, "shape"):
        n_features = n_features.shape[1]

    n = len(y_true)
    r2 = r2_score(y_true, y_pred)
    adj_r2 = 1 - ((1 - r2) * (n - 1) / (n - n_features - 1)) 
    
    return adj_r2