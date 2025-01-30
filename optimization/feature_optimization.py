import logging
from .optimization import optimizeing_features
from utils.print_feature_type import print_features_with_types, compare_features
import pandas as pd


def feature_optimize(data, task, target, direction, n_trials, target_class,
                    test_df, model, categorical_features , fixed_features 
                    ):

    feature_columns = data.drop(columns=[target]).columns.tolist()
    features_to_optimize = [feat for feat in feature_columns if feat not in fixed_features]
    logging.info(f"Features to optimize: {features_to_optimize}")

    # 피처의 최소값과 최대값을 갖고 있는 값들의 최대, 최소로 설정
    feature_bounds = {}
    for feature in features_to_optimize:
        min_val = data[feature].min()
        max_val = data[feature].max()
        feature_bounds[feature] = (min_val, max_val)
    logging.info(f"Feature bounds: {feature_bounds}")

    # 최적화할 샘플 선택 (테스트 데이터셋의 첫 번째 샘플)
    sample_idx = 0
    original_sample = test_df.iloc[sample_idx].drop(labels=[target])
    logging.info(f"Original sample selected: {original_sample.to_dict()}")

    try:
        optimized_features, optimized_prediction = optimizeing_features(
            predictor=model, 
            original_features=original_sample, 
            feature_bounds=feature_bounds, 
            categorical_features=categorical_features,
            task=task,
            direction=direction, 
            n_trials=n_trials,
            target_class=target_class  
        )
        logging.info(f"Optimized features: {optimized_features}")
        logging.info(f"Optimized prediction: {optimized_prediction}")
    except Exception as e:
        logging.error(f"Feature optimization failed: {e}")
        return


    compare_features(original_sample, pd.Series(optimized_features), categorical_features)

    
    optimized_sample = optimized_features.copy()
    for feature in fixed_features:
        if feature in original_sample:
            optimized_sample[feature] = original_sample[feature]
        else:
            logging.warning(f"Fixed feature '{feature}' not found in original sample.")


    try:
        original_prediction_series = model.predict(pd.DataFrame([original_sample.to_dict()]))
        original_prediction = original_prediction_series.iloc[0]
    except KeyError:
        original_prediction = original_prediction_series.values[0]
    except Exception as e:
        logging.error(f"Failed to get original prediction: {e}")
        original_prediction = None

    try:
        optimized_prediction_series = model.predict(pd.DataFrame([optimized_features]))
        optimized_prediction_value = optimized_prediction_series.iloc[0]
    except KeyError:
        optimized_prediction_value = optimized_prediction_series.values[0]
    except Exception as e:
        logging.error(f"Failed to get optimized prediction: {e}")
        optimized_prediction_value = None

    print(f"\nOriginal Prediction: {original_prediction}")
    print(f"Optimized Prediction: {optimized_prediction_value}")

    return original_prediction, optimized_prediction_value
