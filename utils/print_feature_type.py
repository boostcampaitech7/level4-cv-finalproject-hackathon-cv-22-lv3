import pandas as pd


def compare_features(original_features, optimized_features, categorical_features):
    """
    Compare original and optimized features.

    Parameters
        original_features : pd.Series or dict
            Original feature names and values.
        optimized_features : pd.Series or dict
            Optimized feature names and values.
        categorical_features : list
            List of features considered categorical.

    Returns
        str
            A formatted string showing a comparison table of features.
    """
    comparison_df = pd.DataFrame({
        "Feature": original_features.index,
        "Type": [
            "Categorical" if feat in categorical_features else "Numerical"
            for feat in original_features.index
        ],
        "Original": original_features.values,
        "->": "->",
        "Optimized": optimized_features.values,
    })
    return comparison_df.to_string(index=False)