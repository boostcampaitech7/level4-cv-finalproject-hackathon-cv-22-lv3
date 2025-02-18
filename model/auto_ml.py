import pandas as pd
from utils.logger_config import logger
from omegaconf import OmegaConf
import json
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, accuracy_score, f1_score
from autogluon.tabular import TabularPredictor
from imblearn.over_sampling import SMOTE
from model.regression_metrics import adjusted_r2_score
from optimization.feature_optimization import convert_to_serializable


def automl_module(data, task, target, preset, time_to_train, config):
    """
    Run AutoGluon model training.

    Parameters
        data : pd.DataFrame
            Preprocessed dataset.
        task : str
            Type of prediction task; one of "regression", "binary", or "multiclass".
        target : str
            Name of the target variable.
        preset : int
            Quality level for the model preset.
        time_to_train : int
            Maximum training time in seconds.
        config : dict or OmegaConf
            Configuration dictionary containing model settings.

    Returns
        tuple
            A tuple containing:
                - predictor (TabularPredictor): The trained AutoGluon model.
                - test_df (pd.DataFrame): Test dataset.
                - config (dict): Updated configuration with model results.

    Raises
        KeyError
            If the target column is missing from the training data.
        ValueError
            If an unsupported task type is provided.
    """
    if task == "regression":
        train_df, test_df = train_test_split(data, test_size=0.2, random_state=42)
    else:
        train_df, test_df = train_test_split(
            data, test_size=0.2, random_state=42, stratify=data[target]
        )

    if target not in train_df.columns:
        raise KeyError(
            f"Label column '{target}' is missing from training data. "
            f"Training data columns: {list(train_df.columns)}"
        )

    if task in ["binary", "multiclass"]:
        X_train = train_df.drop(columns=[target])
        y_train = train_df[target]
        try:
            sm = SMOTE(random_state=42)
            X_res, y_res = sm.fit_resample(X_train, y_train)
            train_df = pd.concat(
                [
                    pd.DataFrame(X_res, columns=X_train.columns),
                    pd.DataFrame(y_res, columns=[target]),
                ],
                axis=1,
            )
            logger.info("SMOTE applied to balance the training data classes.")
        except Exception as e:
            logger.error(f"Error during SMOTE application: {e}")
            pass

    predictor = TabularPredictor(
        label=target,
        problem_type=task,
        verbosity=2
    ).fit(
        train_data=train_df,
        time_limit=time_to_train,
        presets=preset,
        num_gpus=1
    )

    y_pred = predictor.predict(test_df.drop(columns=[target]))

    if task == "regression":
        mae = mean_absolute_error(test_df[target], y_pred)
        X_test = test_df.drop(columns=[target])
        adv_r2 = adjusted_r2_score(test_df[target], y_pred, X_test)
        logger.info("AutoGluon Regressor results:")
        logger.info(f" - MAE: {mae:.4f}")
        logger.info(f" - Advanced R^2: {adv_r2:.4f}")
        config["model_result"] = {
            "MAE": round(mae, 4),
            "Advanced_R2": round(adv_r2, 4)
        }
    elif task in ["binary", "multiclass"]:
        accuracy = float(accuracy_score(test_df[target], y_pred))
        f1 = float(f1_score(test_df[target], y_pred, average="weighted"))
        logger.info("AutoGluon Classifier results:")
        logger.info(f" - Accuracy: {accuracy:.4f}")
        logger.info(f" - F1 Score: {f1:.4f}")
        config["model_result"] = {
            "accuracy": round(accuracy, 4),
            "f1_score": round(f1, 4)
        }
    else:
        raise ValueError(f"Unsupported task type: {task}")

    leaderboard = predictor.leaderboard(test_df, silent=True)
    logger.info(f"LeaderBoard Result:\n{leaderboard}")
    config["top_models"] = leaderboard.to_dict()

    feature_importance = predictor.feature_importance(test_df)
    logger.info(f"Feature Importance:\n{feature_importance}")
    logger.info("==============================================================")
    config["feature_importance"] = feature_importance.to_dict()

    evaluation = predictor.evaluate(test_df)
    logger.info(f"Evaluation Results:\n{evaluation}")
    logger.info("==============================================================")

    return predictor, test_df, config


def train_model(data, config_path):
    """
    Execute the AutoML pipeline with AutoGluon.

    Parameters
        data : pd.DataFrame
            Preprocessed dataset.
        config_path : str
            Path to the configuration file (in OmegaConf format) containing keys such as
            'task', 'target_feature', 'model_quality', and 'time_to_train'.

    Returns
        tuple :
            - model (TabularPredictor): The trained AutoGluon model.
            - test_df (pd.DataFrame): Test dataset used for evaluation.
    """
    config = OmegaConf.load(config_path)
    model_config = config["model"]
    task = config["task"]
    target = config["target_feature"]
    selected_quality = model_config["model_quality"]
    time_to_train = model_config["time_to_train"]
    preset = f"{selected_quality}_quality"
    try:
        model, test_df, config = automl_module(data, task, target, selected_quality, time_to_train, config)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(
                OmegaConf.to_container(config, resolve=True),
                f,
                indent=4,
                ensure_ascii=False
            )
        logger.info("AutoGluon model class labels:")
        logger.info(model.class_labels)
        logger.info("==========================================")
    except Exception as e:
        logger.error(f"Model training failed: {e}")
        return

    return model, test_df