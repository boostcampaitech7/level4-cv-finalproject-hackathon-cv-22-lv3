import logging
from omegaconf import OmegaConf
from config.config_generator import generate_config
from config.update_config import update_config
from data.model_input_builder import feature_selection, make_filtered_data
from data.data_preprocess import preprocessing
from utils.determine_feature import determine_problem_type
from train.auto_ml import train_model
from optimization.feature_optimization import feature_optimize


def process_1(data_path):
    '''
    웹에서 data_path받아와 user_config, model_config 구성
    user_config는 다시 웹에 전송 (포함 내용 : feature)
    
    model_config -> 서버에서 활용, EDA 결과가 담긴 features로 구성, 웹에서 받아올 config 설정을 미리 지정
    '''    
    model_config_path, user_config_path, original_df = generate_config(data_path)

    return model_config_path, user_config_path, original_df


def process_2(model_config_path, original_df):
    '''
    사용자 정보를 받아 전처리를 진행하고
    '''
    # 사용자한테 받은 dict_type을 통해 모델 config 업데이트
    config_updates = {
        "target_feature": "Attrition",
        "controllable_feature": [
            "MonthlyIncome",
            "WorkLifeBalance"
        ],
        "necessary_feature": [
            "Age",
            "Education",
            "DistanceFromHome",
            "OverTime"
        ],
        "limited_feature" : 6,
        "model" : {
            "time_to_train": 30,
            "model_quality": 0
        }
    }
    
    # 사용자에게 받은 것을 통해 업데이트
    model_config_path = update_config(model_config_path, config_updates)
    # task 업데이트 함수
    determine_problem_type(model_config_path)
    # 사용자에게 입력 받은 것을 바탕으로 모델 config 업데이트 -> corrlation을 통한 final features 생성, 제어변수, 환경변수 업데이트
    feature_selection(model_config_path)
    # 사용자한테서 받아온 feature들을 통해 먼저 전처리해서 dataframe_만들기
    df = make_filtered_data(model_config_path, original_df)
    
    # 전처리 진행
    preprocessed_df, preprocessor = preprocessing(df, model_config_path)
    
    # 학습 진행
    model, test_df = train_model(preprocessed_df, model_config_path)
    
    # user_config 만들어서 보내주기
    '''
    - 학습 결과 → train_result : {}, 학습 진행 후 → 확정
    - 특성 중요도 → feature_importance : {}, 학습 진행 전에도 가능
    - TOP10 모델의 정보 → top_models : {} → 학습 진행 후 → 확정
    - 제어 변수들의 범위 → Categorical, Numeric Type 다르게 설정
    - 타겟 변수의 범위 → Categorical, Numeric
    - 회귀, 분류, Multiclass 등 task : {}, 학습 진행 전에도 가능
    '''

    return model_config_path, model, test_df, preprocessed_df, preprocessor


def process_3(model_config_path, model, test_df, preprocessed_df, preprocessor):    

    logging.info("Starting feature optimization to maximize the target variable...")
    
    model_config = OmegaConf.load(model_config_path)
    controllable_feature = model_config["controllable_feature"]
    
    config_updates = {
        "optimization": {
            "direction": "maximize",
            "n_trials": 30,
            "target_class": 0,
            "opt_range": {
                "MonthlyIncome": [
                    1500,
                    15000
                    ],
                "WorkLifeBalance": [
                    0,
                    3
                    ]} 
        }
    }
    
    model_config_path = update_config(model_config_path, config_updates)
    
    preprocessed_df = preprocessor.decode(preprocessed_df, controllable_feature)

    # 최적화를 진행한다.
    final_dict = feature_optimize(model_config_path, model, preprocessed_df)
    
    return final_dict

## 현준 결과 보내기
    
if __name__ == '__main__':
    data_path = '/data/ephemeral/home/data/WA_Fn-UseC_-HR-Employee-Attrition.csv'
    
    model_config_path, user_config_path, original_df = process_1(data_path)
    
    model_config_path, model, test_df, preprocessed_df, preprocessor = process_2(model_config_path, original_df)
    
    final_dict = process_3(model_config_path, model, test_df, preprocessed_df, preprocessor)