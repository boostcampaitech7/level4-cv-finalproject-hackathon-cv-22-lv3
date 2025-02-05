import logging
from .optimization import optimizeing_features
from utils.print_feature_type import compare_features
import pandas as pd


def feature_optimize(data, task, target, direction, n_trials, target_class,
                    test_df, model, categorical_features , fixed_features, config
                    ):
    """Feature를 변경하면서 모델 최적화를 진행합니다.

    Args:
        data (pd.DataFrame): 전처리된 데이터셋
        task (str): 모델이 수항할 task
        target (str): 최적화할 feature
        direction (str): minimize OR maximize
        n_trials (int): 최적화를 시도할 횟수
        target_class (str): 최적화할 feature의 종류
        test_df (pd.DataFrame): 테스트 데이터셋
        model (Object): 학습된 모델
        categorical_features (str): 카테고리 Feature들의 리스트
        fixed_features (list): 변경 불가능한 feature
        config (dict): 사용자 입력이 포함된 config json파일 

    Returns:
        original_prediction(pd.Series): 실제 feature
        optimized_prediction_value(pd.Series) : 최적화 된 feature

    """

    # feature_columns = data.drop(columns=[target]).columns.tolist()
    # features_to_optimize = [feat for feat in feature_columns if feat not in fixed_features]
    # logging.info(f"Features to optimize: {features_to_optimize}")

    # feature_bounds = {}
    # for feature in features_to_optimize:
    #     min_val = data[feature].min()
    #     max_val = data[feature].max()
    #     feature_bounds[feature] = (min_val, max_val)
    feature_bounds = config["opt_range"]
    # logging.info(f"Feature bounds: {feature_bounds}")

    sample_idx = 0
    original_sample = test_df.iloc[sample_idx].drop(labels=[target])
    # logging.info(f"Original sample selected: {original_sample.to_dict()}")

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


    comparison_df = compare_features(original_sample, pd.Series(optimized_features), categorical_features)

    
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

    return comparison_df, original_prediction, optimized_prediction_value
