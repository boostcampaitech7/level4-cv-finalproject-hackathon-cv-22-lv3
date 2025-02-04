import logging
from optimization.auto_ml import train_model
from utils.determine_feature import categorical_feature
from utils.config import load_config, parse_arguments
from utils.setting import data_setting, visualization_feature
from optimization.feature_optimization import feature_optimize
from preprocessing.data_preprocessing import base_preprocessing
import pandas as pd
from utils.user_input import save_config_to_json
from user_input.login import create_userinfo
from user_input.data_upload import upload_dataset
from data.data_info import get_json
from user_input.base_setting import user_base_setting

def main_pipline():
    """
    전체적인 파이프라인을 관리합니다.
    [data load -> 전처리 -> 예측 모델 학습 -> feature optimization]
    """

    user_name, user_email = create_userinfo() # 로그인
    data_path = upload_dataset() # 데이터 업로드
    json_file_path, eda_html_path = get_json(user_name, user_email, data_path) # 업로드된 데이터 EDA 진행 및 반환 가능

    features = visualization_feature(json_file_path)
    controllable_feature,necessary_feature, target_feature,limited_feature =  user_base_setting(features)

    save_config_to_json(user_name, user_email, data_path, controllable_feature, necessary_feature, target_feature, limited_feature)

    print(f'controllable_feature : {controllable_feature}')
    print(f'necessary_feature : {necessary_feature}')
    print(f'target_feature : {target_feature}')
    print(f'limited_feature : {limited_feature}')




    # logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # args = parse_arguments()  # 예: --config 옵션이 존재함

    # # 만약 --config 옵션에 특별한 키워드(예: "interactive")를 주면
    # # 사용자 입력을 통해 config를 생성하도록 할 수 있습니다.
    # if args.config.lower() == "interactive":
    #     config, config_file = create_config_from_input()
    # else:
    #     try:
    #         config = load_config(args.config)
    #         logging.info(f"Configuration loaded from {args.config}")
    #     except Exception as e:
    #         logging.error(f"Failed to load configuration: {e}")
    #         return


    # data, target, fixed_features, selected_quality, time_to_train, n_trials = data_setting(config)

    # # step1 : EDA를 반환한다.
    # json_file_path, task, data, direction, target_class, eda_html_path = base_preprocessing(config, data, target)

    # model, test_df = train_model(data, task, target, selected_quality, time_to_train)

    # categorical_features = categorical_feature(data, json_file_path)
    # logging.info("Starting feature optimization to maximize the target variable...")

    # comparison_df, original_prediction, optimized_prediction_value = feature_optimize(
    #     data, task, target, direction, n_trials, target_class, test_df,
    #     model, categorical_features, fixed_features )
    
    # return comparison_df, original_prediction, optimized_prediction_value

    
if __name__ == '__main__':
    main_pipline()