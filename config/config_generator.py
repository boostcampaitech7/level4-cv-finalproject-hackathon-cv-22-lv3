import json
from utils.logger_config import logger
import pandas as pd
import os.path as osp
from datetime import datetime, timezone, timedelta
from omegaconf import OmegaConf
from ydata_profiling import ProfileReport
from utils.analysis_feature import identify_categorical_features


def generate_config(data_path):
    """
    Generate configuration files for model training and update user settings.

    This function loads the dataset from the given path, performs exploratory
    data analysis (EDA) using ydata_profiling, and generates two configuration
    files:
      - A user configuration file for web communication.
      - A model configuration file for internal server use.
    It also saves an HTML report of the EDA.

    Parameters
        data_path : str
            Path to the input CSV data file.

    Returns
        tuple
            A tuple containing:
                - model_config_path (str): Path to the generated model configuration file.
                - user_config_path (str): Path to the generated user configuration file.
                - data (pd.DataFrame): Loaded dataset.
    """
    save_path = osp.dirname(data_path)

    try:
        data = pd.read_csv(data_path)
        logger.info(f"Data loaded from {data_path}")
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        return

    # Create a timestamp using KST (UTC+9)
    kst = timezone(timedelta(hours=9))
    timestamp = datetime.now(kst).strftime("%Y%m%d_%H%M%S")

    # Define file names and paths
    user_config_filename = f"{timestamp}_user_config.json"
    model_config_filename = "model_config.json"
    eda_html_filename = "EDA_analysis.html"

    user_config_path = osp.join(save_path, user_config_filename)
    model_config_path = osp.join(save_path, model_config_filename)
    eda_html_path = osp.join(save_path, eda_html_filename)

    # Drop columns with only a single unique value.
    for col in data.columns:
        if len(data[col].unique()) == 1:
            data.drop(columns=[col], inplace=True)

    # Generate EDA report and save as HTML.
    profile = ProfileReport(data, explorative=True)
    profile.to_file(eda_html_path)

    # Convert the EDA report to an OmegaConf object.
    original_eda_str = profile.to_json()
    original_eda_dict = json.loads(original_eda_str)
    original_eda = OmegaConf.create(original_eda_dict)

    # Filter the EDA results.
    filtered_data = _extract_filtered_eda(original_eda)
    correlations = original_eda.get("correlations")
    categorical_feature = identify_categorical_features(filtered_data)

    config = OmegaConf.create({})

    # Create user configuration for web communication.
    user_config = OmegaConf.merge(
        config,
        OmegaConf.create({
            "model_config_path": model_config_path,
            "eda_html_path": eda_html_path,
            "features": list(data.columns)
        })
    )

    with open(user_config_path, "w", encoding="utf-8") as f:
        json.dump(
            OmegaConf.to_container(user_config, resolve=True),
            f,
            indent=4,
            ensure_ascii=False
        )

    model_config = OmegaConf.merge(
        config,
        OmegaConf.create({
            "data_path": data_path,
            "save_path": save_path,
            "features": list(data.columns),
            "filtered_data": filtered_data,
            "correlations": correlations,
            "correlations_result": None,
            "final_features": None,
            "categorical_features": categorical_feature,
            "model_result": {},
            "top_models": {},
            "feature_importance": {},
        })
    )

    with open(model_config_path, "w", encoding="utf-8") as f:
        json.dump(
            OmegaConf.to_container(model_config, resolve=True),
            f,
            indent=4,
            ensure_ascii=False
        )

    logger.info(f"User config saved: {user_config_path}")
    logger.info(f"Model config saved: {model_config_path}")
    logger.info(f"EDA HTML saved: {eda_html_path}")

    return model_config_path, user_config_path, data


def _extract_filtered_eda(config):
    """
    Extract and filter relevant EDA information from the full report.

    Parameters
        config : OmegaConf
            OmegaConf object containing the full EDA report.

    Returns
        dict
            Dictionary with filtered statistics for each variable.
    """
    filtered_data = {
        var_name: {
            "type": info.get("type"),
            "p_missing": info.get("p_missing"),
            "n_distinct": info.get("n_distinct"),
            "p_distinct": info.get("p_distinct"),
            "mean": info.get("mean"),
            "std": info.get("std"),
            "variance": info.get("variance"),
            "min": info.get("min"),
            "max": info.get("max"),
            "kurtosis": info.get("kurtosis"),
            "skewness": info.get("skewness"),
            "mad": info.get("mad"),
            "range": info.get("range"),
            "iqr": info.get("iqr"),
            "Q1": info.get("25%"),
            "Q3": info.get("75%")
        }
        for var_name, info in config.get("variables", {}).items()
    }
    return filtered_data


if __name__ == "__main__":
    data_path = "/data/ephemeral/home/uploads/WA_Fn-UseC_-HR-Employee-Attrition.csv"
    generate_config(data_path)