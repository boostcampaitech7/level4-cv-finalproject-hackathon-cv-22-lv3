import optuna
import pandas as pd
from autogluon.tabular import TabularPredictor
import logging


def optimizeing_features(predictor: TabularPredictor,
                         original_features: pd.Series,
                         feature_bounds: dict,
                         categorical_features: list,
                         task: str,
                         direction: str,
                         n_trials: int = 100,
                         target_class: str = None):
    """
    Optimize features of a sample to maximize or minimize the target prediction.

    Parameters
        predictor : TabularPredictor
            Trained AutoGluon TabularPredictor model.
        original_features : pd.Series
            Original feature values of the sample.
        feature_bounds : dict
            Dictionary with lower and upper bounds for each feature.
        categorical_features : list
            List of features considered categorical.
        task : str
            Task type; one of 'regression', 'binary', or 'multiclass'.
        direction : str
            Optimization direction; either 'maximize' or 'minimize'.
        n_trials : int, optional
            Number of optimization trials (default is 100).
        target_class : str, optional
            Target class for binary or multiclass tasks (default is None).

    Returns
        tuple
            A tuple containing:
                - best_features (dict): Optimized feature values.
                - best_prediction (float): Prediction with optimized features.
                - original_prediction (float): Prediction with original features.
                - improvement (float): Improvement achieved.
    """
    if direction not in ['maximize', 'minimize']:
        raise ValueError("Direction must be either 'maximize' or 'minimize'")
    if task not in ['regression', 'binary', 'multiclass']:
        raise ValueError("Task must be one of 'regression', 'binary', or 'multiclass'")

    original_df = pd.DataFrame([original_features.to_dict()])
    if task in ['binary', 'multiclass']:
        proba = predictor.predict_proba(original_df)
        local_target_class = target_class
        if task == 'binary':
            if local_target_class is None:
                local_target_class = predictor.class_labels[1]
        else:
            if local_target_class is None:
                local_target_class = predictor.class_labels[-1]
        if local_target_class not in predictor.class_labels:
            raise ValueError(
                f"target_class '{local_target_class}' not found in model's class labels."
            )
        class_index = predictor.class_labels.index(local_target_class)
        original_prediction = proba.iloc[0, class_index]
    else:
        original_prediction = predictor.predict(original_df).iloc[0]

    def objective(trial):
        modified_features = original_features.copy()
        for feature, (low, high) in feature_bounds.items():
            if feature in categorical_features:
                modified_features[feature] = trial.suggest_int(feature, low, high)
            else:
                if low == high:
                    current_value = original_features[feature]
                    bound1 = current_value * (1 - low / 100.0)
                    bound2 = current_value * (1 + high / 100.0)
                    low_bound = min(bound1, bound2)
                    high_bound = max(bound1, bound2)
                else:
                    if low > high:
                        low, high = high, low
                    low_bound, high_bound = low, high
                modified_features[feature] = trial.suggest_uniform(
                    feature, low_bound, high_bound
                )
        modified_df = pd.DataFrame([modified_features.to_dict()])
        if task in ['binary', 'multiclass']:
            proba = predictor.predict_proba(modified_df)
            local_tc = target_class
            if task == 'binary':
                if local_tc is None:
                    local_tc = predictor.class_labels[1]
            else:
                if local_tc is None:
                    local_tc = predictor.class_labels[-1]
            class_index_ = predictor.class_labels.index(local_tc)
            return proba.iloc[0, class_index_]
        else:
            return predictor.predict(modified_df).iloc[0]

    study = optuna.create_study(direction=direction)
    study.optimize(objective, n_trials=n_trials)
    best_trial = study.best_trial
    best_features = original_features.copy()
    for feature in feature_bounds.keys():
        if feature in categorical_features:
            best_features[feature] = int(best_trial.params[feature])
        else:
            best_features[feature] = best_trial.params[feature]
    best_prediction = best_trial.value
    if direction == 'maximize':
        improvement = best_prediction - original_prediction
    else:
        improvement = original_prediction - best_prediction
    return best_features.to_dict(), best_prediction, original_prediction, improvement