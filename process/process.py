from omegaconf import OmegaConf
from config.config_generator import generate_config
from config.update_config import update_config
from data.model_input_builder import feature_selection, make_filtered_data
from data.data_preprocess import preprocessing
from utils.determine_feature import determine_problem_type
from utils.user_feature import user_feature
from model.auto_ml import train_model
from optimization.feature_optimization import feature_optimize
from utils.logger_config import logger
from gpt import gpt_solution


def process_1(data_path):
    """Load data and generate configuration files.

    Parameters
    ----------
    data_path : str
        Path to the input data.

    Returns
    -------
    tuple
        A tuple containing:
            - model_config_path (str): Path to the model configuration file.
            - user_config_path (str): Path to the user configuration file.
            - original_df (pandas.DataFrame): Loaded input data.
    """
    logger.info(f"📂 데이터 로드 시작: {data_path}")
    model_config_path, user_config_path, original_df = generate_config(data_path)
    logger.info("✅ 데이터 로드 완료")
    return model_config_path, user_config_path, original_df


def process_2(model_config_path, user_config_path, original_df):
    """Update configuration, preprocess data, and train the model.

    Parameters
    ----------
    model_config_path : str
        Path to the model configuration file.
    user_config_path : str
        Path to the user configuration file.
    original_df : pandas.DataFrame
        The original input data.

    Returns
    -------
    tuple
        A tuple containing:
            - updated model_config_path (str)
            - updated user_config_path (str)
            - model: Trained model object.
            - preprocessed_df (pandas.DataFrame): Preprocessed data.
            - preprocessor: Preprocessing object.
    """
    logger.info("📊 사용자 설정을 업데이트합니다...")
    config_updates = {
        "target_feature": "Attrition",
        "controllable_feature": ["MonthlyIncome", "WorkLifeBalance"],
        "necessary_feature": ["Age", "Education", "DistanceFromHome", "OverTime"],
        "limited_feature": 10,
        "model": {"time_to_train": 100, "model_quality": "best"}
    }
    model_config_path = update_config(model_config_path, config_updates)
    determine_problem_type(model_config_path)
    logger.info("🎯 Feature Selection 진행 중...")
    feature_selection(model_config_path)
    df = make_filtered_data(model_config_path, original_df)
    logger.info("🛠 데이터 전처리 시작...")
    preprocessed_df, preprocessor = preprocessing(df, model_config_path)
    logger.info("🚀 모델 학습 시작...")
    model, _ = train_model(preprocessed_df, model_config_path)
    logger.info("✅ 모델 학습 완료")
    update_config_info = user_feature(df, model_config_path)
    user_config_path = update_config(user_config_path, update_config_info)
    return model_config_path, user_config_path, model, preprocessed_df, preprocessor


def process_3(model_config_path, user_config_path, model, preprocessed_df, preprocessor):
    """Perform feature optimization using the trained model.

    Parameters
        model_config_path : str
            Path to the model configuration file.
        user_config_path : str
            Path to the user configuration file.
        model : object
            Trained model.
        preprocessed_df : pandas.DataFrame
            Preprocessed data.
        preprocessor : object
            Preprocessing object used to decode the data.

    Returns
        tuple
            A tuple containing:
                - final_dict (dict): Results from feature optimization.
                - user_config_path (str): Updated user configuration file path.
    """
    logger.info("🔍 Feature Optimization 시작...")
    model_config = OmegaConf.load(model_config_path)
    controllable_feature = model_config["controllable_feature"]
    config_updates = {
        "optimization": {
            "direction": "maximize",
            "n_trials": 15,
            "target_class": 0,
            "opt_range": {
                "MonthlyIncome": [20, 20],
                "WorkLifeBalance": [0, 3]
            }
        }
    }
    model_config_path = update_config(model_config_path, config_updates)
    logger.info("📉 데이터 디코딩 진행 중...")
    preprocessed_df = preprocessor.decode(preprocessed_df, controllable_feature)
    print("\n\n------------------Decoding-----------------")
    print(preprocessed_df)
    print("\n\n")
    logger.info("⚡ 최적화 알고리즘 실행...")
    final_dict = feature_optimize(model_config_path, user_config_path, model, preprocessed_df)
    logger.info("✅ Feature Optimization 완료!")
    return final_dict, user_config_path


if __name__ == "__main__":
    data_path = "/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-22-lv3/base_merged_data.csv"
    logger.info("🚀 AutoML 파이프라인 실행 시작!")
    model_config_path, user_config_path, original_df = process_1(data_path)
    model_config_path, user_config_path, model, preprocessed_df, preprocessor = process_2(
        model_config_path, user_config_path, original_df
    )
    final_dict, user_config_path = process_3(
        model_config_path, user_config_path, model, preprocessed_df, preprocessor
    )
    logger.info("🏁 전체 프로세스 완료!")
    result_json = gpt_solution(final_dict, model_config_path, user_config_path)
    print("이것은 이제 최종 result json입니다람쥐")
    print(result_json)