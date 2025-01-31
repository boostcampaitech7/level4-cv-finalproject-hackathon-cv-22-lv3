def data_setting(config):
    """
    데이터를 불러오고, 모델 학습 및 최적화에 필요한 설정 값들을 추출하는 함수입니다.

    Args:
        config (dict): 설정 정보를 담고 있는 딕셔너리.

    Returns:
        data(pd.DataFrame): 불러온 데이터
        target(str): 타깃 변수 이름
        fixed_feature(list): 최적화에서 제외될 피처 목록
        selected_quality(str): 선택된 모델 품질 옵션
        time_to_train(int): 모델 학습 시간(초) 제한
        n_trials(int): 최적화 시도 횟수
    """
    data_path = config.get('data_path')
    target = config.get('target')

    try:
        data = pd.read_csv(data_path)
        logging.info(f"Data loaded from {data_path}")
    except Exception as e:
        logging.error(f"Failed to load data: {e}")
        return

    user_fixed_features = config.get('user_fixed_features', [])
    fixed_features = list(set(user_fixed_features))
    logging.info(f"Fixed Features (Not to be optimized): {fixed_features}")

    quality_map = config.get('quality_map')
    selected_quality = quality_map.get(config.get('selected_quality', 0), "Invalid selection")
    if selected_quality == "Invalid selection":
        logging.error("Invalid quality selection. Please choose a valid option from quality_map.")
        return
    logging.info(f"Selected quality: {selected_quality}")

    time_to_train = config.get('time_to_train', 500)
    n_trials = config.get('n_trials', 100)

    return data, target, fixed_features, selected_quality, time_to_train, n_trials