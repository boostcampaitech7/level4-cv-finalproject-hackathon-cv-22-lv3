from optimization.auto_ml import train_model
from utils.determine_feature import determine_problem_type, make_filtered_data
from utils.config import load_config, parse_arguments
from utils.setting import data_setting, visualization_feature
from optimization.feature_optimization import feature_optimize
from utils.user_input import save_config_to_json, add_config_to_json
from user_input.login import create_userinfo
from user_input.data_upload import upload_dataset
from user_input.setting_input import user_base_setting, model_base_setting, base_optimize_setting
from utils.determine_feature import feature_selection
from utils.analysis_feature import identify_categorical_features
from utils.determine_feature import categorical_feature

import logging
from config.config_generator import generate_config
from config.update_config import update_config
from omegaconf import OmegaConf
from data.data_preprocess import preprocessing
import pandas as pd


def process_1(data_path):
    '''
    웹에서 data_path받아와 user_config, model_config 구성
    user_config는 다시 웹에 전송 (포함 내용 : feature)
    
    model_config -> 서버에서 활용, EDA 결과가 담긴 features로 구성, 웹에서 받아올 config 설정을 미리 지정
    '''    
    model_config_path, user_config_path = generate_config(data_path)

    return model_config_path, user_config_path


def process_2(user_config_path, model_config_path):
    '''
    사용자 정보를 받아 전처리를 진행하고
    '''
    # 사용자한테 받은 dict_type을 통해 모델 config 업데이트
    user_config = OmegaConf.load(user_config_path)
    config_updates = {
        "target_feature": "test",
        "controllabel_feature": "test",
        "necessary_feature": "test",
        "limited_feature" : "test",
        }
    
    # 사용자에게 받은 것을 통해 업데이트
    model_config_path = update_config(model_config_path, config_updates)
    # 사용자에게 입력 받은 것을 바탕으로 모델 config 업데이트 -> corrlation을 통한 final features 생성, 제어변수, 환경변수 업데이트
    feature_selection(model_config_path)
    # 사용자한테서 받아온 feature들을 통해 먼저 전처리해서 dataframe_만들기
    df = make_filtered_data(model_config_path)
    # 전처리 진행
    preprocessed_df = preprocessing(df, model_config_path)
    
    # user_config 만들어서 보내주기
    # control 변수 -> 민, 맥스 값 | 
    # 현준이한테 필요한 사항 물어보기
    
    return


def process_3():
    # 사용자한테 train_time, model_qualuity 입력 받디
    # dict로 
    update_config
    
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

## 현준 결과 보내기
    
if __name__ == '__main__':
    main_pipline()