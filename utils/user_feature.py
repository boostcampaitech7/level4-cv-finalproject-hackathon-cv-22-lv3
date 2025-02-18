import pandas as pd
import numpy as np
from omegaconf import OmegaConf


def user_feature(data, model_config_path):
    """
    Extract and update feature information for web transmission.

    Parameters
        data : pd.DataFrame
            The original dataset.
        model_config_path : str
            Path to the model configuration file.

    Returns
        dict
            A dictionary containing task info, correlations, controllable and target
            feature ranges, model results, leaderboard, and feature importance.
    """
    update_config_dict = {
        "task": None,
        "correlations_result": None,
        "controllable_range": {},
        "target_range": {},
        "model_result": None,
        "top_models": None,
        "feature_importance": None,
    }
    config = OmegaConf.load(model_config_path)
    filtered_data = config["filtered_data"]
    task = config["task"]
    correlations_result = config["correlations_result"]
    controllable_feature = config["controllable_feature"]
    target_feature = config["target_feature"]
    model_result = config["model_result"]
    top_models = config["top_models"]
    feature_importance = config["feature_importance"]

    update_config_dict["task"] = task
    update_config_dict["correlations_result"] = correlations_result

    if len(controllable_feature) == 1:
        col = controllable_feature[0]
        info = extract_feature_range(data, filtered_data, col)
        update_config_dict["controllable_range"][col] = info
    else:
        for col in controllable_feature:
            info = extract_feature_range(data, filtered_data, col)
            update_config_dict["controllable_range"][col] = info

    if target_feature:
        info = extract_feature_range(data, filtered_data, target_feature)
        update_config_dict["target_range"][target_feature] = info

    update_config_dict["model_result"] = model_result
    update_config_dict["top_models"] = top_models
    update_config_dict["feature_importance"] = feature_importance

    return update_config_dict


def extract_feature_range(data, filtered_data, feature):
    """
    Extract the range and data type of a feature based on EDA results and raw data.

    Parameters
        data : pd.DataFrame
            The original dataset.
        filtered_data : dict
            Filtered EDA information containing feature statistics.
        feature : str
            The name of the feature to process.

    Returns
        list or None
            A list with range and type information or None if not applicable.
    """
    col_type = filtered_data[feature].get("type", None)
    if col_type in ["Categorical", "Boolean"]:
        if not np.issubdtype(data[feature].dtype, np.integer):
            str_range = sorted(data[feature].unique())
            int_range = list(range(len(str_range)))
            return [str_range, int_range, col_type, "str"]
        else:
            int_range = sorted(map(int, data[feature].unique()))
            return [int_range, col_type, "int"]
    elif col_type == "Numeric":
        min_val = filtered_data[feature].get("min", data[feature].min())
        max_val = filtered_data[feature].get("max", data[feature].max())
        return [[min_val, max_val], "Numeric"]
    return None


if __name__ == "__main__":
    df = pd.read_csv("/data/ephemeral/home/uploads/WA_Fn-UseC_-HR-Employee-Attrition.csv")
    model_config_path = "/data/ephemeral/home/uploads/model_config.json"
    update_config_result = user_feature(df, model_config_path)
    print(update_config_result)