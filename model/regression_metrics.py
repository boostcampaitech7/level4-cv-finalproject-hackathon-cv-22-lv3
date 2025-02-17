from sklearn.metrics import r2_score


def adjusted_r2_score(y_true, y_pred, n_features):
    """
    Calculate the adjusted R² score.

    Parameters
        y_true : array-like
            True target values.
        y_pred : array-like
            Predicted target values.
        n_features : int or pd.DataFrame
            Number of independent variables or a DataFrame containing the independent variables.

    Returns
        float
            The adjusted R² score.
    """
    if hasattr(n_features, "shape"):
        n_features = n_features.shape[1]
    n = len(y_true)
    r2 = r2_score(y_true, y_pred)
    adj_r2 = 1 - ((1 - r2) * (n - 1) / (n - n_features - 1))
    return adj_r2