import logging
from auto_ml import train_model
from determine_feature import categorical_feature
from utils.config import load_config, parse_arguments
from setting import data_setting
from optimization.feature_optimization import feature_optimize
from preprocessing.data_preprocessing import base_preprocessing

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    args = parse_arguments()

    try:
        config = load_config(args.config)
        logging.info(f"Configuration loaded from {args.config}")
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        return

    data, target, fixed_features, selected_quality, time_to_train, n_trials = data_setting(config)

    task, data, direction, target_class = base_preprocessing(config, data, target)

    model, test_df = train_model(data, task, target, selected_quality, time_to_train)

    categorical_features = categorical_feature(data, threshold=10)
    logging.info("Starting feature optimization to maximize the target variable...")

    original_prediction, optimized_prediction_value = feature_optimize(
        data, task, target, direction, n_trials, target_class, test_df, model, categorical_features, fixed_features
    )

if __name__ == '__main__':
    main()