import logging
from .optimization import optimizeing_features
from utils.print_feature_type import compare_features
from omegaconf import OmegaConf
import pandas as pd

def feature_optimize(config_path, model, test_df):
    """Feature를 변경하면서 모델 최적화를 진행합니다.

    Args:
        task (str): 모델이 수행할 task (regression/binary/multiclass)
        config (dict): 사용자 입력이 포함된 config (json) 파일
            - config['target_feature'] : 예측(학습) 대상 컬럼명
            - config['optimization'] : 아래 내용을 포함
                * 'direction': minimize or maximize
                * 'n_trials': Optuna 최적화 반복 횟수
                * 'target_class': 분류 문제에서 최적화할 클래스
                * 'opt_range': 변경 가능 Feature 범위 딕셔너리
        test_df (pd.DataFrame): 테스트(검증) 데이터
        model (TabularPredictor or 유사 객체): 학습된 모델
        categorical_features (list): 카테고리형 Feature 리스트
        fixed_features (list): 변경 불가능한 Feature 리스트

    Returns:
        comparison_df (pd.DataFrame): 변경 전/후 Feature 비교표
        original_prediction (float): 변경 전 모델 예측값
        optimized_prediction_value (float): 최적화된 Feature로부터 얻은 예측값
    """

    # ===========================
    # 1) 설정값 가져오기
    # ===========================
    config = OmegaConf.load(config_path)
    
    task = config.get("task")
    categorical_features = config.get("categorical_features")
    fixed_features = config.get("necessary_feature")
    target = config.get("target_feature")            # (예: 'Attrition')
    
    opt_config = config['optimization']
    direction = opt_config['direction']         # (예: 'maximize' or 'minimize')
    n_trials = opt_config['n_trials']           # (예: 100)
    target_class = opt_config['target_class']   # (예: 'Yes' or '1' 등)
    feature_bounds = opt_config["opt_range"]    # 최적화 대상 Feature의 min-max 범위

    logging.info(f"Features to optimize: {list(feature_bounds.keys())}")
    logging.info(f"Feature bounds: {feature_bounds}")
    
    # ================================================================
    # 2) target_class와 다른 값을 갖는 데이터만 필터링 (test_df 축소)
    # ================================================================
    # 예: target_feature='Attrition', target_class='No' 라면, 
    #     test_df[Attrition != 'No'] 행들만 남긴다.
    filtered_df = test_df[test_df[target] != target_class]
    
    if filtered_df.empty:
        # 필터링 후 남은 행이 하나도 없는 경우
        logging.error(
            f"No rows found where '{target}' != '{target_class}'. "
            "Cannot proceed with feature optimization."
        )
        return None, None, None  # 혹은 적절한 처리를 할 수 있음
    
    # =================================================================
    # 3) (샘플 1개 선택) 여기서는 예시로 sample_idx=0 행을 사용
    # =================================================================
    sample_idx = 0  # 원하는대로 바꿔도 됨
    original_sample = filtered_df.iloc[sample_idx].drop(labels=[target])
    logging.info(f"Original sample selected (index={filtered_df.index[sample_idx]}): {original_sample.to_dict()}")

    # ==============================
    # 4) feature 최적화 수행 (Optuna)
    # ==============================
    try:
        # 3개 값을 반환하도록 구현된 optimizeing_features 함수
        optimized_features, optimized_prediction, original_prediction,  improvement = optimizeing_features(
            predictor=model, 
            original_features=original_sample, 
            feature_bounds=feature_bounds, 
            categorical_features=categorical_features,
            task=task,
            direction=direction, 
            n_trials=n_trials,
            target_class=target_class  
        )
        logging.info(f"Optimized features: {optimized_features}")
        logging.info(f"Original 확률값: {original_prediction}")
        logging.info(f"Optimized 확률값: {optimized_prediction}")
        logging.info(f"Improvement from original: {improvement:.4f}")
    except Exception as e:
        logging.error(f"Feature optimization failed: {e}")
        # 예외 발생 시 None 반환(혹은 다른 에러 처리 로직)
        return None, None, None

    # =====================================
    # 5) 변경 전후 Feature를 비교하기
    # =====================================
    # compare_features: (original_series, optimized_series, categorical_features) → 비교표 DataFrame
    comparison_df = compare_features(original_sample, pd.Series(optimized_features), categorical_features)

    # =================================================
    # 6) 최적화에서 제외할 피처(fixed_features) 원복
    # =================================================
    optimized_sample = optimized_features.copy()
    for feature in fixed_features:
        if feature in original_sample:
            optimized_sample[feature] = original_sample[feature]
        else:
            logging.warning(f"Fixed feature '{feature}' not found in original sample.")

    # ================================================
    # 7) (Optional) 변경 전/후 최종 모델 예측값 계산
    # ================================================
    try:
        original_prediction_series = model.predict(pd.DataFrame([original_sample.to_dict()]))
        original_prediction = original_prediction_series.iloc[0]
    except KeyError:
        # 예측 결과의 인덱스 혹은 컬럼 Key 문제로 발생 가능
        original_prediction = original_prediction_series.values[0]
    except Exception as e:
        logging.error(f"Failed to get original prediction: {e}")
        original_prediction = None

    try:
        optimized_prediction_series = model.predict(pd.DataFrame([optimized_sample]))
        optimized_prediction_value = optimized_prediction_series.iloc[0]
    except KeyError:
        optimized_prediction_value = optimized_prediction_series.values[0]
    except Exception as e:
        logging.error(f"Failed to get optimized prediction: {e}")
        optimized_prediction_value = None

    print(f"\nOriginal Prediction: {original_prediction}")
    print(f"Optimized Prediction: {optimized_prediction_value}")

    # 최종 결과물 반환
    return comparison_df, original_prediction, optimized_prediction_value, improvement