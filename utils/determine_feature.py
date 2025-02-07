import pandas as pd
from utils.analysis_feature import identify_categorical_features
import logging
import json
from utils.config import load_config

def determine_problem_type(data, config, threshold=10):
    """해당 Task가 어떤 종류의 Task인지 구분합니다.

    Args:
        data (csv): 학습할 데이터를 받아옵니다.
        target (string): 목표로 하는 Feature를 의미합니다.
        threshold (int, optional): threshold 보다 적은 고유 종류를 갖는다면 다중분류 문제로 분류합니다. Defaults to 10.

    Raises:
        ValueError: target이 학습 데이터에 존재하지 않는 경우

    Returns:
        string: 해당 task의 종류
    """
    target = config["target_feature"]
    if target not in data.columns:
        print(f'column들 리스트 {data.columns}')
        raise ValueError(f"타겟 컬럼 '{target}'이 데이터에 존재하지 않습니다.")
    
    target_series = data[target]
    
    if pd.api.types.is_numeric_dtype(target_series):
        num_unique = target_series.nunique()
        if num_unique <= 2:
            print('\n=================해당 task는 binary classification 입니다.=================\n')
            return 'binary'
        elif num_unique <= threshold:
            print('\n=================해당 task는 multiclass 입니다.=================\n')
            return 'multiclass'
        else:
            print('\n================해당 task는 Regression 입니다.=================\n')
            return 'regression'
    else:
        num_unique = target_series.nunique()
        if num_unique == 2:
            print('\n=================해당 task는 binary classification 입니다.=================\n')
            return 'binary'
        elif num_unique > 2:
            print('\n=================해당 task는 multiclass 입니다.=================\n')
            return 'multiclass'
        else:
            raise ValueError(f"타겟 컬럼 '{target}'은(는) 고유 값이 하나뿐입니다.")



def categorical_feature(config, json_file_path):    
    try:
        categorical_features = identify_categorical_features(json_file_path)
        # categorical_features = identify_categorical_features(config,10)

        logging.info(f"Identified categorical features: {categorical_features}")
    except Exception as e:
        logging.error(f"Failed to identify categorical features: {e}")
        return
    return categorical_features


def feature_selection(file_path, feature_len=100):
    # JSON 파일 읽기
    config = load_config(file_path)
    target_feature = config.get("target_feature")
    controllable_feature = config.get("controllable_feature")
    environment_feature = config.get("necessary_feature")
    
    # limited_feature가 -1이면, 제한 없이 feature_len 개수로 설정합니다.
    limited_feature = config.get("limited_feature")
    if limited_feature == -1:
        limited_feature = feature_len
    print(f'총 설명변수의 개수: {limited_feature}\n\n')

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

    print(f'정렬 전 candidate_correlations: {candidate_correlations}\n\n')
    # target_feature와의 상관계수 절대값 기준 내림차순 정렬
    candidate_correlations = dict(sorted(candidate_correlations.items(), key=lambda x: x[1], reverse=True))
    print(f'정렬 후 candidate_correlations: {candidate_correlations}\n\n')

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
    print(f'controlled data : {controllable_feature}')
    print('\n\n')
    print(f'ENV data : {environment_feature}')

    # final_features에 모델 훈련에 사용되는 모든 변수를 저장합니다. 
    final_features = controllable_feature + environment_feature
    config["final_features"] = final_features
    print(f'\n\nfinal_features: {final_features}')

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

    return controllable_feature, environment_feature


def make_filtered_data(json_file):
    """
    JSON 파일에 기록된 data_path를 이용해 CSV 데이터를 로드한 후,
    controllable_feature, necessary_feature, target_feature, Added_feature에 해당하는 열만 선택하여 DataFrame으로 반환합니다.
    
    Args:
        json_file_path (str): JSON 파일 경로
        
    Returns:
        pd.DataFrame: 선택된 열로 구성된 DataFrame
    """
    # JSON 파일 읽기
    with open(json_file, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    # data_path를 이용해 CSV 파일 로드
    data_path = config.get("data_path")
    if not data_path:
        raise ValueError("JSON 파일에 'data_path' 항목이 없습니다.")
    
    df = pd.read_csv(data_path)
    
    # 선택할 feature들을 각각 추출 (각 항목은 리스트 혹은 단일 문자열일 수 있음)
    controllable = config.get("controllable_feature", [])
    necessary = config.get("necessary_feature", [])
    target = config.get("target_feature")
    added = config.get("Added_feature", [])
    
    # 각 항목이 단일 문자열이면 리스트로 변환
    if isinstance(controllable, str):
        controllable = [controllable]
    if isinstance(necessary, str):
        necessary = [necessary]
    if isinstance(added, str):
        added = [added]
    
    # 네 항목의 feature들을 집합으로 결합 (중복 제거)
    selected_features = set(controllable) | set(necessary) | set(added)
    if target:  # target_feature는 반드시 포함
        selected_features.add(target)
    
    # 실제 CSV 파일에 존재하는 열만 선택 (없는 열은 무시)
    available_features = [col for col in selected_features if col in df.columns]
    filtered_df = df[available_features].copy()
    
    return filtered_df





# 사용 예시
if __name__ == "__main__":
    file_path = "/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-22-lv3/ydata_profiling/0207_1043_config.json"  # JSON 파일 경로
    ctr_feature, env_feature = feature_selection(file_path)
    print("==========================================")
    print(f"✅ Controllable Features: {ctr_feature}")
    print(f"✅ Environment Features: {env_feature}")
