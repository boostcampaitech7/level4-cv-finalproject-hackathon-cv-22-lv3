import json
import pandas as pd
from typing import List, Tuple
from omegaconf import OmegaConf
from utils.logger_config import logger


def feature_selection(config_path: str, feature_len: int = 100) -> Tuple[List[str], List[str]]:
    '''
    Summary:
        주어진 설정 파일을 기반으로 최적의 feature 조합을 선택하는 함수.
        target feature와의 상관계수를 기준으로 중요 변수를 선정.
        제한된 feature 개수(limited_feature)에 따라 feature selection을 수행.
    
    Args:
        config_path (str): 설정 파일(.json)의 경로
        feature_len (int, optional): 기본 제한 feature 개수 (기본값: 100)
    
    Returns:
        Tuple[List[str], List[str]]:
        controllable_final (List[str]): 제어 가능한 변수 목록.
        other_final (List[str]): 환경 변수 목록.
    '''
    config = OmegaConf.load(config_path)
    target_feature = config.get("target_feature")
    controllable_feature = config.get("controllable_feature", [])
    environment_feature = config.get("necessary_feature", [])
    
    limited_feature = config.get("limited_feature")
    
    if limited_feature == -1:
        limited_feature = feature_len
    
    logger.info(f'총 설명변수의 개수 : {limited_feature}')

    correlations_list = config.get("correlations", {}).get("auto", [])
    
    if not correlations_list:
        logger.info("correlations -> auto 항목이 비어 있습니다.")
        controllable_final = controllable_feature
        other_final = list(set(environment_feature) - set(controllable_final))
        
        return controllable_final, other_final

    candidate_correlations = {}

    for idx, corr_dict in enumerate(correlations_list):
        if corr_dict[target_feature] == 1.0:
            for k, v in corr_dict.items():
                candidate_correlations[k] = v

    candidate_correlations = dict(sorted(candidate_correlations.items(), key=lambda x: x[1], reverse=True))
    
    config["correlations_result"] = candidate_correlations

    final_features = controllable_feature + environment_feature
    limited_feature -= len(controllable_feature)
    candidates = list(candidate_correlations.keys())
    
    for feature in candidates[1:]:
        if len(environment_feature) >= limited_feature:
            break
        if feature not in final_features:
            environment_feature.append(feature)

    logger.info(f"controlled data : {controllable_feature}")
    logger.info(f"ENV data : {environment_feature}")

    final_features = controllable_feature + environment_feature
    config["final_features"] = final_features
    logger.info(f"final_features: {final_features}")
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(OmegaConf.to_container(config, resolve=True), f, indent=4, ensure_ascii=False)


def make_filtered_data(config_path: str, data: pd.DataFrame) -> pd.DataFrame:
    '''
    Summary:
        설정 파일(config_path)에 정의된 feature 목록을 기반으로 데이터를 필터링하는 함수
        설정 파일에 포함된 controllable_feature, necessary_feature, target_feature, final_features를 기준으로 열을 선택

    Args:
        config_path (str): 설정 파일(.json 또는 .yaml)의 경로.
        data (pd.DataFrame): 필터링할 원본 데이터.
        
    Returns:
        pd.DataFrame: 설정된 feature만 포함한 데이터프레임.
    '''
    config = OmegaConf.load(config_path)
        
    controllable = config.get("controllable_feature", [])
    necessary = config.get("necessary_feature", [])
    target = config.get("target_feature")
    final = config.get("final_features", [])
    
    if isinstance(controllable, str):
        controllable = [controllable]
    if isinstance(necessary, str):
        necessary = [necessary]
    if isinstance(final, str):
        final = [final]
    
    selected_features = set(controllable) | set(necessary) | set(final)
    
    if target:
        selected_features.add(target)
    
    available_features = [col for col in selected_features if col in data.columns]
    filtered_df = data[available_features].copy()
    
    return filtered_df