import pandas as pd
import logging


def data_setting(config):

    # 데이터 경로 설정 및 타겟 설정
    data_path = config.get('data_path')
    target = config.get('target')

    # 데이터 불러오기
    try:
        data = pd.read_csv(data_path)
        logging.info(f"Data loaded from {data_path}")
    except Exception as e:
        logging.error(f"Failed to load data: {e}")
        return

    # # 자동으로 고정할 피처 감지
    # try:
    #     auto_fixed_features = auto_determine_fixed_features(data, target)
    #     logging.info(f"Automatically determined fixed features: {auto_fixed_features}")
    # except Exception as e:
    #     logging.error(f"Failed to determine fixed features: {e}")
    #     return

    # # 사용자 지정 피처 고정 추가
    # user_fixed_features = config.get('user_fixed_features', [])
    # fixed_features = list(set(auto_fixed_features + user_fixed_features))
    # logging.info(f"Fixed Features (Not to be optimized): {fixed_features}")


    user_fixed_features = config.get('user_fixed_features', [])
    fixed_features = list(set(user_fixed_features))
    logging.info(f"Fixed Features (Not to be optimized): {fixed_features}")

    # 모델 품질 매핑 및 선택
    quality_map = config.get('quality_map', {
        0: "best_quality",
        1: "high_quality",
        2: "good_quality",
        3: "medium_quality"
    })
    selected_quality = quality_map.get(config.get('selected_quality', 0), "Invalid selection")
    if selected_quality == "Invalid selection":
        logging.error("Invalid quality selection. Please choose a valid option from quality_map.")
        return
    logging.info(f"Selected quality: {selected_quality}")

    # 모델 학습 시간 및 최적화 시도 횟수 설정
    time_to_train = config.get('time_to_train', 500)
    n_trials = config.get('n_trials', 100)


    return data, target, fixed_features, selected_quality, time_to_train, n_trials