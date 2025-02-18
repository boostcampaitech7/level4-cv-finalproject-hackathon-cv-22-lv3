from typing import Tuple, Optional, Dict
import pandas as pd
from autogluon.tabular import TabularPredictor
from omegaconf import OmegaConf
from config.config_generator import generate_config
from config.update_config import update_config
from data.data_preprocess import preprocessing
from data.model_input_builder import feature_selection, make_filtered_data
from utils.determine_feature import determine_problem_type
from utils.update_user_feature import update_user_feature
from utils.logger_config import logger
from utils.gpt import gpt_solution
from model.auto_ml import train_model
from optimization.feature_optimization import feature_optimize
from utils.gpt import gpt_solution


def process_1(data_path: str) -> Tuple[str, str, pd.DataFrame]:
    '''
    Summary:
        데이터 경로를 받아 user_config 및 model_config를 생성하는 함수
        user_config는 웹에 전송되며, feature 정보를 포함.
        model_config는 서버에서 활용되며, EDA 결과 및 웹에서 받을 설정 정보를 사전에 구성.
    
    Args:
        data_path (str): 원본 데이터 파일의 경로.

    Returns:
        Tuple[str, str, pd.DataFrame]:
            model_config_path (str): 생성된 모델 설정 파일 경로.
            user_config_path (str): 생성된 사용자 설정 파일 경로.
            original_df (pd.DataFrame): 로드된 원본 데이터.
    '''
    logger.info("🚀 AutoML 파이프라인 실행 시작!")
    logger.info(f"📂 데이터 로드 시작: {data_path}")  
    model_config_path, user_config_path, original_df = generate_config(data_path)
    logger.info("✅ 데이터 로드 완료")
    
    return model_config_path, user_config_path, original_df


def process_2(model_config_path: str, 
              user_config_path: str, 
              original_df: pd.DataFrame,
              config_updates: Optional[Dict] = None) -> Tuple[str, str, TabularPredictor, pd.DataFrame, object]:
    '''
    Summary:
        사용자 설정을 기반으로 데이터 전처리 및 모델 학습을 수행하는 함수.
    
    Args:
        model_config_path (str): 모델 설정 파일 경로.
        user_config_path (str): 사용자 설정 파일 경로.
        original_df (pd.DataFrame): 원본 데이터셋.
        config_updates (Optional[Dict], default=None): 모델 설정을 업데이트할 선택적 딕셔너리.

    Returns:
        Tuple[str, str, TabularPredictor, pd.DataFrame, object]:
            model_config_path (str): 업데이트된 모델 설정 파일 경로.
            user_config_path (str): 업데이트된 사용자 설정 파일 경로.
            model (TabularPredictor): 학습된 AutoML 모델 객체.
            preprocessed_df (pd.DataFrame): 전처리된 데이터셋.
            preprocessor (object): 데이터 전처리기 객체.
    '''
    logger.info("📊 사용자 설정을 업데이트합니다...")
    
    if config_updates:
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
    
    update_config_info = update_user_feature(df, model_config_path)
    user_config_path = update_config(user_config_path, update_config_info)

    return model_config_path, user_config_path, model, preprocessed_df, preprocessor


def process_3(model_config_path: str, 
              user_config_path: str, 
              model: TabularPredictor, 
              preprocessed_df: pd.DataFrame, 
              preprocessor,
              config_updates: Optional[Dict] = None) -> Tuple[Dict, str]:  
    '''
    Summary:
        모델 학습 이후 Feature Optimization을 수행하고, GPT 솔루션을 통해 실행 전략을 생성하는 함수.
    
    Args:
        model_config_path (str): 모델 설정 파일 경로.
        user_config_path (str): 사용자 설정 파일 경로.
        model (TabularPredictor): 학습된 AutoML 모델 객체.
        preprocessed_df (pd.DataFrame): 전처리된 데이터셋.
        preprocessor (object): 데이터 디코딩 및 전처리를 수행하는 객체.
        config_updates (Optional[Dict], default=None): 모델 설정을 업데이트할 선택적 딕셔너리.

    Returns:
        str:
            user_config_path (str): 전체 프로세스가 완료된 사용자 설정 파일 경로.
    '''
    if config_updates:
        model_config_path = update_config(model_config_path, config_updates)
        user_config_path = update_config(user_config_path, config_updates)

    logger.info("🔍 Feature Optimization 시작...")

    model_config = OmegaConf.load(model_config_path)
    controllable_feature = model_config["controllable_feature"]
    
    logger.info("📉 데이터 디코딩 진행 중...")
    preprocessed_df = preprocessor.decode(preprocessed_df, controllable_feature)

    logger.info("⚡ 최적화 알고리즘 실행...")
    final_dict = feature_optimize(model_config_path, user_config_path, model, preprocessed_df)
    
    logger.info("✅ Feature Optimization 완료!")
    logger.info("🧠 GPT 솔루션 실행...")
    
    user_config_path = gpt_solution(final_dict, model_config_path, user_config_path)

    logger.info("🏁 전체 프로세스 완료!")

    return user_config_path