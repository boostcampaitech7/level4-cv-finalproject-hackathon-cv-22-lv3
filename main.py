import logging
from optimization.auto_ml import train_model
from utils.determine_feature import categorical_feature
from utils.config import load_config, parse_arguments
from utils.setting import data_setting
from optimization.feature_optimization import feature_optimize
from preprocessing.data_preprocessing import base_preprocessing
import pandas as pd

def main_pipline():
    """
        전체적인 파이프라인을 관리합니다.
        [data load -> 전처리 -> 예측 모델 학습 -> feature optimization] 
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    args = parse_arguments()

    try:
        config = load_config(args.config)
        logging.info(f"Configuration loaded from {args.config}")
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        return

    data, target, fixed_features, selected_quality, time_to_train, n_trials = data_setting(config)

    json_file_path, task, data, direction, target_class = base_preprocessing(config, data, target)

    model, test_df = train_model(data, task, target, selected_quality, time_to_train)

    categorical_features = categorical_feature(data, json_file_path)
    logging.info("Starting feature optimization to maximize the target variable...")

    comparison_df, original_prediction, optimized_prediction_value = feature_optimize(
        data, task, target, direction, n_trials, target_class, test_df,
        model, categorical_features, fixed_features )
    
    return comparison_df, original_prediction, optimized_prediction_value

    
if __name__ == '__main__':
    main_pipline()