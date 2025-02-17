import json
from utils.logger_config import logger
from omegaconf import OmegaConf
import numpy as np


def convert_numpy_types(data):
    """
    Recursively convert NumPy data types in the input to native Python types.

    Parameters
        data : any
            Data to be converted, which may include dicts, lists, or NumPy scalars.

    Returns
        any
            Data with all NumPy types replaced by native Python types.
    """
    if isinstance(data, dict):
        return {k: convert_numpy_types(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_numpy_types(item) for item in data]
    elif isinstance(data, np.generic):
        return data.item()
    else:
        return data


def update_config(config_path, config_updates):
    """
    Load a configuration file, merge it with updates, and write the updated configuration.

    Parameters
        config_path : str
            Path to the configuration file.
        config_updates : dict
            Dictionary of configuration updates.

    Returns
        str
            The path to the updated configuration file.
    """
    try:
        config = OmegaConf.load(config_path)
        logger.info(f"Loaded configuration from: {config_path}")
    except FileNotFoundError:
        logger.warning("Configuration file not found.")
    
    config_updates = convert_numpy_types(config_updates)
    updated_config = OmegaConf.merge(config, OmegaConf.create(config_updates))
    
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(
            OmegaConf.to_container(updated_config, resolve=True),
            f,
            indent=4,
            ensure_ascii=False
        )
        logger.info(f"Updated configuration saved to: {config_path}")
    
    return config_path


if __name__ == "__main__":
    config_path = "/data/ephemeral/home/uploads/model_config.json"
    config_updates = {
        "target_feature": "test",
        "controllabel_feature": "test",
        "necessary_feature": "test",
        "limited_feature": "test"
    }
    
    update_config(config_path, config_updates)