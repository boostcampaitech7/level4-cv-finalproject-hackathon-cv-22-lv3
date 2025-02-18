from omegaconf import OmegaConf
import pandas as pd
from config.update_config import update_config
from utils.logger_config import logger


def determine_problem_type(config_path, threshold=10):
    """
    Determine the problem type (binary, multiclass, or regression) based on the target
    feature in the dataset and update the configuration accordingly.

    Parameters
        config_path : str
            Path to the configuration file.
        threshold : int, optional
            Maximum number of unique values for a numeric target to be considered multiclass,
            by default 10.

    Raises
        ValueError
            If the target feature is not present in the dataset or if it has only one unique value.
    """
    config = OmegaConf.load(config_path)
    target = config["target_feature"]
    data = pd.read_csv(config["data_path"])

    if target not in data.columns:
        raise ValueError(f"Target column '{target}' is not present in the dataset.")

    target_series = data[target]
    num_unique = target_series.nunique()

    if pd.api.types.is_numeric_dtype(target_series):
        if num_unique <= 2:
            logger.info("Setting task: binary classification")
            update_config(config_path, {"task": "binary"})
        elif num_unique <= threshold:
            logger.info("Setting task: multiclass classification")
            update_config(config_path, {"task": "multiclass"})
        else:
            logger.info("Setting task: regression")
            update_config(config_path, {"task": "regression"})
    else:
        if num_unique == 2:
            logger.info("Setting task: binary classification")
            update_config(config_path, {"task": "binary"})
        elif num_unique > 2:
            logger.info("Setting task: multiclass classification")
            update_config(config_path, {"task": "multiclass"})
        else:
            raise ValueError(f"Target column '{target}' has only one unique value.")