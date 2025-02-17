import json
import pandas as pd
from omegaconf import OmegaConf
from utils.logger_config import logger


def feature_selection(config_path, feature_len=100):
    """
    Select features for model training based on configuration and correlation data.

    Parameters
        config_path : str
            Path to the configuration file.
        feature_len : int, optional
            Default maximum number of features if limited_feature is set to -1, by default 100.

    Returns
        tuple or None
            If no correlation data is found, returns a tuple of (controllable features, other features);
            otherwise, updates the configuration file and returns None.
    """
    config = OmegaConf.load(config_path)
    target_feature = config.get("target_feature")
    controllable_feature = config.get("controllable_feature", [])
    environment_feature = config.get("necessary_feature", [])
    limited_feature = config.get("limited_feature")
    if limited_feature == -1:
        limited_feature = feature_len
    logger.info(f"총 설명변수의 개수 : {limited_feature}")

    correlations_list = config.get("correlations", {}).get("auto", [])
    if not correlations_list:
        logger.info("correlations -> auto 항목이 비어 있습니다.")
        controllable_final = controllable_feature
        other_final = list(set(environment_feature) - set(controllable_final))
        return controllable_final, other_final

    candidate_correlations = {}
    for _, corr_dict in enumerate(correlations_list):
        if corr_dict[target_feature] == 1.0:
            for k, v in corr_dict.items():
                candidate_correlations[k] = v

    candidate_correlations = dict(
        sorted(candidate_correlations.items(), key=lambda x: x[1], reverse=True)
    )
    config["correlations_result"] = candidate_correlations

    final_features = controllable_feature + environment_feature
    limited_feature -= len(controllable_feature)
    candidates = list(candidate_correlations.keys())
    for feature in candidates[1:]:
        if len(environment_feature) >= limited_feature:
            break
        if feature not in final_features:
            environment_feature.append(feature)

    logger.info(f"controlled data : {controllable_feature}")
    logger.info(f"ENV data : {environment_feature}")

    final_features = controllable_feature + environment_feature
    config["final_features"] = final_features
    logger.info(f"final_features: {final_features}")

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(
            OmegaConf.to_container(config, resolve=True),
            f,
            indent=4,
            ensure_ascii=False,
        )


def make_filtered_data(config_path, data):
    """
    Filter the dataset based on feature selections in the configuration.

    Parameters
    config_path : str
        Path to the configuration file.
    data : pd.DataFrame
        The dataset to be filtered.

    Returns
    pd.DataFrame
        A DataFrame containing only the selected features.
    """
    config = OmegaConf.load(config_path)
    controllable = config.get("controllable_feature", [])
    necessary = config.get("necessary_feature", [])
    target = config.get("target_feature")
    final = config.get("final_features", [])

    if isinstance(controllable, str):
        controllable = [controllable]
    if isinstance(necessary, str):
        necessary = [necessary]
    if isinstance(final, str):
        final = [final]

    selected_features = set(controllable) | set(necessary) | set(final)
    if target:
        selected_features.add(target)

    available_features = [col for col in selected_features if col in data.columns]
    filtered_df = data[available_features].copy()

    return filtered_df