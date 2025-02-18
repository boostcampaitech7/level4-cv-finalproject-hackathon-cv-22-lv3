import logging
import pandas as pd
import numpy as np
from .optimization import optimizeing_features
from utils.print_feature_type import compare_features
from omegaconf import OmegaConf
from utils.logger_config import logger
from config.update_config import update_config


def feature_optimize(model_config_path, user_config_path, model, test_df):
    """
    Optimize model features based on configuration settings.

    This function adjusts feature values to improve model predictions.
    Depending on the task type ('regression' or 'classification') specified in
    the configuration file, it applies different optimization strategies and
    returns a dictionary summarizing the results.

    Parameters
        model_config_path : str
            Path to the model configuration file in OmegaConf format.
        user_config_path : str
            Path to the user configuration file that will be updated with the results.
        model : object
            Trained model with a predict() method.
        test_df : pandas.DataFrame
            DataFrame containing test or validation data.

    Returns
        dict or None
            For regression tasks, returns a dictionary with keys:
                - 'task': 'regression'
                - 'results': List of optimization results per sample.
                - 'average_improvement': Average improvement value.
            For classification tasks, returns a dictionary with keys:
                - 'task': 'classification'
                - 'target_class': The target class optimized for.
                - 'results': List of optimization results per sample.
                - 'count_changed_to_target': Number of samples changed to the target class.
                - 'ratio_changed_to_target': Ratio of samples changed to the target class.
            Returns None if classification optimization cannot proceed.
    """
    config = OmegaConf.load(model_config_path)
    task = config.get("task")
    categorical_features = config.get("categorical_features")
    X_features = config.get("final_features")
    target = config.get("target_feature")
    opt_config = config["optimization"]
    direction = opt_config["direction"]
    n_trials = opt_config["n_trials"]
    target_class = opt_config["target_class"]
    feature_bounds = opt_config["opt_range"]

    logging.info(f"Features to optimize: {list(feature_bounds.keys())}")
    logging.info(f"Feature bounds: {feature_bounds}")

    if task == "regression":
        if len(test_df) < 5:
            logging.warning("test_df has fewer than 5 rows; using the entire dataset.")
            sample_df = test_df.copy()
        else:
            sample_df = test_df.sample(n=5, random_state=42)
            print(sample_df)

        results_list = []
        for idx, row_data in sample_df.iterrows():
            original_sample = row_data.drop(labels=[target])
            logging.info(f"[Regression] index={idx}, sample={original_sample.to_dict()}")

            try:
                best_features, best_pred, orig_pred, improvement = optimizeing_features(
                    predictor=model,
                    original_features=original_sample,
                    feature_bounds=feature_bounds,
                    categorical_features=categorical_features,
                    task=task,
                    direction=direction,
                    n_trials=n_trials,
                    target_class=target_class,
                )
                logging.info(f"[Regression] index={idx}")
                logging.info(f"   Original pred:  {orig_pred}")
                logging.info(f"   Optimized pred: {best_pred}")
                logging.info(f"   Improvement:    {improvement}")

                comparison_df = compare_features(
                    original_sample, pd.Series(best_features), categorical_features
                )

                optimized_sample = best_features.copy()
                for feat in X_features:
                    if feat in original_sample:
                        optimized_sample[feat] = original_sample[feat]

                final_prediction = model.predict(
                    pd.DataFrame([optimized_sample])
                ).iloc[0]

                results_list.append(
                    {
                        "index": idx,
                        "comparison_df": comparison_df,
                        "original_prediction": float(orig_pred),
                        "optimized_prediction": float(best_pred),
                        "improvement": float(improvement),
                        "final_prediction": float(final_prediction),
                    }
                )
            except Exception as e:
                logging.error(f"Optimization failed on index={idx}: {e}")
                results_list.append({"index": idx, "error": str(e)})

        valid_improvements = [
            r["improvement"] for r in results_list if "improvement" in r
        ]
        avg_improvement = (
            sum(valid_improvements) / len(valid_improvements)
            if valid_improvements
            else None
        )

        final_dict = {
            "task": "regression",
            "results": results_list,
            "average_improvement": float(avg_improvement),
        }

        update_config(user_config_path, final_dict)
        return final_dict

    else:
        preds = model.predict(test_df.drop(columns=[target], errors="ignore"))
        test_df["predicted_class"] = preds
        filtered_df = test_df[test_df["predicted_class"] != target_class].copy()

        if filtered_df.empty:
            logger.error(
                f"No rows found where predicted_class != '{target_class}'. Cannot proceed."
            )
            return None

        if len(filtered_df) <= 10:
            sample_df = filtered_df
        else:
            sample_df = filtered_df.sample(n=10, random_state=42)

        results_list = []
        for idx, row_data in sample_df.iterrows():
            original_sample = row_data.drop(labels=[target, "predicted_class"], errors="ignore")
            logger.info(f"[Classification] Optimizing sample idx={idx}: {original_sample.to_dict()}")

            try:
                best_feat, best_pred, orig_pred, improvement = optimizeing_features(
                    predictor=model,
                    original_features=original_sample,
                    feature_bounds=feature_bounds,
                    categorical_features=categorical_features,
                    task=task,
                    direction=direction,
                    n_trials=n_trials,
                    target_class=target_class,
                )
            except Exception as e:
                logger.error(f"Optimization failed for index {idx}: {e}")
                continue

            comparison_df = compare_features(
                original_sample, pd.Series(best_feat), categorical_features
            )
            logger.info(comparison_df, extra={"force": True})

            try:
                orig_df = pd.DataFrame([original_sample.to_dict()])
                orig_pred_class = model.predict(orig_df).iloc[0]
                optimized_df = pd.DataFrame([best_feat])
                new_pred_class = model.predict(optimized_df).iloc[0]
            except Exception as e:
                logger.error(f"Prediction failed after optimization: {e}")
                continue

            logger.info(
                f"[Classification] Index={idx} Original pred_class={orig_pred_class}, "
                f"Optimized pred_class={new_pred_class}, Improvement={improvement:.4f}"
            )

            results_list.append(
                {
                    "index": idx,
                    "original_sample": original_sample.to_dict(),
                    "optimized_features": best_feat,
                    "original_prediction": float(orig_pred),
                    "best_prediction": float(best_pred),
                    "original_pred_class": int(orig_pred_class),
                    "optimized_pred_class": int(new_pred_class),
                    "improvement": float(improvement),
                    "comparison": comparison_df,
                }
            )

        count_changed_to_target = sum(
            1 for r in results_list if r["optimized_pred_class"] == target_class
        )
        total_optimized = len(results_list)
        ratio = count_changed_to_target / total_optimized if total_optimized > 0 else 0.0

        logger.info(
            f"[Classification] {total_optimized} samples optimized; "
            f"{count_changed_to_target} changed to '{target_class}' "
            f"({ratio:.2%})."
        )

        final_dict = {
            "task": "classification",
            "target_class": target_class,
            "results": results_list,
            "count_changed_to_target": count_changed_to_target,
            "ratio_changed_to_target": ratio,
        }

        update_config(user_config_path, final_dict)
        return final_dict


def convert_to_serializable(obj):
    """
    Convert numpy numeric types to native Python types for JSON serialization.

    Parameters
        obj : any
            The object to be converted.

    Returns
        int or float
            The converted Python numeric type if the input is a numpy integer or float.

    Raises
        TypeError
            If the object is not a numpy numeric type.
    """
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")