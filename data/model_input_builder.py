import json
import logging
import pandas as pd
from omegaconf import OmegaConf
from config.update_config import update_config

def categorical_feature(config, json_file_path):    
    try:
        categorical_features = identify_categorical_features(json_file_path)
        # categorical_features = identify_categorical_features(config,10)

        logging.info(f"Identified categorical features: {categorical_features}")
    except Exception as e:
        logging.error(f"Failed to identify categorical features: {e}")
        return
    return categorical_features


def feature_selection(config_path, feature_len=100):
    config = OmegaConf.load(config_path)
    target_feature = config.get("target_feature")
    controllable_feature = config.get("controllable_feature")
    environment_feature = config.get("necessary_feature")
    
    # limited_feature가 -1이면, 제한 없이 feature_len 개수로 설정합니다.
    limited_feature = config.get("limited_feature")
    if limited_feature == -1:
        limited_feature = feature_len
    #print(f"총 설명변수의 개수: {limited_feature}\n\n")
    logging.info(f'총 설명변수의 개수 : {limited_feature}')

    correlations_list = config.get("correlations", {}).get("auto", [])
    if not correlations_list:
        print("correlations -> auto 항목이 비어 있습니다.")
        # controllable feature와 나머지 feature를 구분하여 리턴합니다.
        # 단, correlations 데이터가 없으므로 기본 필수 feature만 전달합니다.
        controllable_final = controllable_feature
        other_final = list(set(environment_feature) - set(controllable_final))
        return controllable_final, other_final

    candidate_correlations = {}

    # correlations_list의 각 딕셔너리에서 target_feature와의 상관계수를 추출합니다.
    for idx, corr_dict in enumerate(correlations_list):
        if corr_dict[target_feature] == 1.0:
            for k, v in corr_dict.items():
                candidate_correlations[k] = v

    print(f"정렬 전 candidate_correlations: {candidate_correlations}\n\n")
    # target_feature와의 상관계수 절대값 기준 내림차순 정렬
    candidate_correlations = dict(sorted(candidate_correlations.items(), key=lambda x: x[1], reverse=True))
    print(f"정렬 후 candidate_correlations: {candidate_correlations}\n\n")

    # 최종 Feature 리스트 구성: 우선 필수 feature를 포함하고, 상관관계가 높은 순서대로 추가합니다.
    final_features = controllable_feature + environment_feature
    limited_feature -= len(controllable_feature)
    candidates = list(candidate_correlations.keys())
    for feature in candidates[1:]:
        if len(environment_feature) >= limited_feature:
            break
        if feature not in final_features:
            environment_feature.append(feature)

    # controllable_features에 포함되는 feature와 나머지 feature로 분리합니다.
    print(f"controlled data : {controllable_feature}")
    print("\n\n")
    print(f"ENV data : {environment_feature}")

    # final_features에 모델 훈련에 사용되는 모든 변수를 저장합니다. 
    final_features = controllable_feature + environment_feature
    config["final_features"] = final_features
    print(f"\n\nfinal_features: {final_features}")
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(OmegaConf.to_container(config, resolve=True), f, indent=4, ensure_ascii=False)

    #return controllable_feature, environment_feature


def make_filtered_data(config_path):
    """
    JSON 파일에 기록된 data_path를 이용해 CSV 데이터를 로드한 후,
    controllable_feature, necessary_feature, target_feature, Added_feature에 해당하는 열만 선택하여 DataFrame으로 반환합니다.
    
    Args:
        json_file_path (str): JSON 파일 경로
        
    Returns:
        pd.DataFrame: 선택된 열로 구성된 DataFrame
    """
    # JSON 파일 읽기
    config = OmegaConf.load(config_path)

    # data_path를 이용해 CSV 파일 로드
    data_path = config.get("data_path")
    if not data_path:
        raise ValueError("JSON 파일에 "data_path" 항목이 없습니다.")
    
    df = pd.read_csv(data_path)
    
    # 선택할 feature들을 각각 추출 (각 항목은 리스트 혹은 단일 문자열일 수 있음)
    controllable = config.get("controllable_feature", [])
    necessary = config.get("necessary_feature", [])
    target = config.get("target_feature")
    final = config.get("final_features", [])
    
    # 각 항목이 단일 문자열이면 리스트로 변환
    if isinstance(controllable, str):
        controllable = [controllable]
    if isinstance(necessary, str):
        necessary = [necessary]
    if isinstance(final, str):
        final = [final]
    
    # 네 항목의 feature들을 집합으로 결합 (중복 제거)
    selected_features = set(controllable) | set(necessary) | set(final)
    if target:  # target_feature는 반드시 포함
        selected_features.add(target)
    
    # 실제 CSV 파일에 존재하는 열만 선택 (없는 열은 무시)
    available_features = [col for col in selected_features if col in df.columns]
    filtered_df = df[available_features].copy()
    
    return filtered_df