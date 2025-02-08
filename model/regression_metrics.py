from sklearn.metrics import r2_score


def adjusted_r2_score(y_true, y_pred, n_features):
    """
    summary: 조정된 R² (Adjusted R²) 값을 계산하는 함수

    args:
        y_true (array-like): 실제 값 (정답 레이블)
        y_pred (array-like): 예측 값
        n_features (int): 독립 변수(특성)의 개수

    return:
        float: 조정된 R² 값
    """
    n = len(y_true)  # 샘플 개수
    r2 = r2_score(y_true, y_pred)  # R² 계산
    adj_r2 = 1 - ((1 - r2) * (n - 1) / (n - n_features - 1))  # 조정된 R² 계산
    return adj_r2
