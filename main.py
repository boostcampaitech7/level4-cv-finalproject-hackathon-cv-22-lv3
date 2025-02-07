import logging
from optimization.auto_ml import train_model
from utils.determine_feature import determine_problem_type, make_filtered_data
from utils.config import load_config, parse_arguments
from utils.setting import data_setting, visualization_feature
from optimization.feature_optimization import feature_optimize
from preprocessing.data_preprocessing import base_preprocessing
import pandas as pd
from utils.user_input import save_config_to_json, add_config_to_json
from user_input.login import create_userinfo
from user_input.data_upload import upload_dataset
from data.data_info import get_json
from user_input.setting_input import user_base_setting, model_base_setting, base_optimize_setting
from utils.determine_feature import feature_selection
from utils.analysis_feature import identify_categorical_features
from utils.determine_feature import categorical_feature

def main_pipline():
    """
    전체적인 파이프라인을 관리합니다.
    [data load -> 전처리 -> 예측 모델 학습 -> feature optimization]
    """

    user_name, user_email = create_userinfo() # 로그인

    data_path = upload_dataset() # 데이터 업로드

    json_file_path, eda_html_path = get_json(user_name, user_email, data_path) # 업로드된 데이터 EDA 진행 및 반환 가능


    all_features, numeric_key_features = visualization_feature(json_file_path) 
    user_settings =  user_base_setting(all_features, numeric_key_features)  # 환경변수, 제어변수, 타겟변수, 갯수 설정

    file_path, config = save_config_to_json(user_name, user_email, data_path, user_settings) # config 파일 설정

    ctr_feature, env_feature = feature_selection(file_path, len(features)) # 제어변수, 환경변수 따로 가져오기
    data_frame = make_filtered_data(file_path) # 사용할 변수들만 포함된 데이터프레임

    task = determine_problem_type(data_frame, config) # task 설정
    model_config = model_base_setting(task) # train_time, model_quality 입력
    config = add_config_to_json(file_path, model_config) # json에 추가로 작성하기

    merged_file_path, processed_df, preprocessor = base_preprocessing(data_frame, file_path) # 데이터 전처리
    config = load_config(merged_file_path)

    # 모델 학습을 위한 train_to_time, quality, task 필요
    model, test_df = train_model(processed_df, config)

    # 카테고리컬 feature를 구분한다.
    categorical_features = categorical_feature(data_frame, merged_file_path)
    logging.info("Starting feature optimization to maximize the target variable...")


    opt_config = base_optimize_setting(config)
    config = add_config_to_json(merged_file_path, opt_config)

    test_df = preprocessor.decode(processed_df, ctr_feature)

    # 최적화를 진행한다.
    comparison_df, original_prediction, optimized_prediction_value = feature_optimize(
        task, config, test_df,
        model, categorical_features, env_feature)
    
    return comparison_df, original_prediction, optimized_prediction_value

    
if __name__ == '__main__':
    main_pipline()