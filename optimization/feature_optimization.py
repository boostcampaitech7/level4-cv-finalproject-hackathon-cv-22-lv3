import numpy as np
import pandas as pd
from omegaconf import OmegaConf
from utils.logger_config import logger
from config.update_config import update_config
from utils.print_feature_type import compare_features
from optimization.optimization import optimizing_features


def feature_optimize(model_config_path: str, 
                     user_config_path: str, 
                     model, test_df: pd.DataFrame) -> dict:
    '''
    Summary:
        Feature 조정을 통해 모델 최적화를 수행하는 함수.
        Regression 또는 Classification 문제에서 feature 값을 변경하면 성능 최적화를 수행함.
        Optuna를 활용한 최적화 기법을 적용.

    Args:
        model_config_path (str): 모델 설정 파일(.json)의 경로.
        user_config_path (str): 사용자 설정 파일(.json)의 경로.
        model (TabularPredictor): 학습된 AutoML 모델.
        test_df (pd.DataFrame): 테스트 데이터프레임.

    Returns:
        dict: 최적화 결과가 포함된 딕셔너리.    
    '''
    config = OmegaConf.load(model_config_path)
    
    task = config.get("task")
    categorical_features = config.get("categorical_features")
    X_features = config.get("final_features")
    target = config.get("target_feature")
    
    opt_config = config['optimization']
    direction = opt_config['direction']         
    n_trials = opt_config['n_trials']           
    target_class = opt_config['target_class']   
    feature_bounds = opt_config["opt_range"]    

    logger.info(f"Features to optimize: {list(feature_bounds.keys())}")
    logger.info(f"Feature bounds: {feature_bounds}")

    if task == 'regression':
        # test_df에서 최대 5개 샘플을 무작위 추출(5개 미만이면 전부 사용)
        if len(test_df) < 5:
            logger.warning("test_df 행 개수가 5개 미만. 전체를 사용합니다.")
            sample_df = test_df.copy()
        else:
            sample_df = test_df.sample(n=5, random_state=42)
            print(sample_df)
        
        results_list = []

        for idx, row_data in sample_df.iterrows():
            # 행에서 타깃(target) 제외한 feature만 추출
            original_sample = row_data.drop(labels=[target])
            logger.info(f"[Regression] index={idx}, sample={original_sample.to_dict()}")

            try:
                # optimizing_features가 4개 반환한다고 가정
                # (best_features, best_pred, orig_pred, improvement)
                best_features, best_pred, orig_pred, improvement = optimizing_features(
                    predictor=model, 
                    original_features=original_sample, 
                    feature_bounds=feature_bounds, 
                    categorical_features=categorical_features,
                    task=task,
                    direction=direction, 
                    n_trials=n_trials,
                    target_class=target_class  
                )

                logger.info(f"[Regression] index={idx}")
                logger.info(f"   Original pred:  {orig_pred}")
                logger.info(f"   Optimized pred: {best_pred}")
                logger.info(f"   Improvement:    {improvement}")

                # 변경 전/후 Feature 비교
                comparison_df = compare_features(
                    original_sample, 
                    pd.Series(best_features), 
                    categorical_features
                )

                # 고정 Feature 복원
                optimized_sample = best_features.copy()
                for feat in X_features:
                    if feat in original_sample:
                        optimized_sample[feat] = original_sample[feat]

                # (Optional) 최종 예측
                final_prediction = model.predict(pd.DataFrame([optimized_sample])).iloc[0]

                # 결과 리스트에 저장
                results_list.append({
                    'index': idx,
                    'comparison_df': comparison_df,
                    'original_prediction': float(orig_pred),
                    'optimized_prediction': float(best_pred),
                    'improvement': float(improvement),
                    'final_prediction': float(final_prediction)
                })

            except Exception as e:
                logger.error(f"Optimization failed on index={idx}: {e}")
                results_list.append({
                    'index': idx,
                    'error': str(e)
                })
        
        # 평균 개선도
        valid_improvements = [r['improvement'] for r in results_list if 'improvement' in r]
        avg_improvement = sum(valid_improvements)/len(valid_improvements) if valid_improvements else None

        # 최종 딕셔너리 반환
        final_dict = {
            'task': 'regression',
            'results': results_list,
            'average_improvement': float(avg_improvement)
        }
        
        update_config(user_config_path, final_dict)
        
        return final_dict

    else: 
        preds = model.predict(test_df.drop(columns=[target], errors='ignore'))  # target 컬럼이 있으면 제외 후 예측
        test_df['predicted_class'] = preds
        filtered_df = test_df[test_df['predicted_class'] != target_class].copy()
        
        if filtered_df.empty:
            logger.error(f"No rows found where predicted_class != '{target_class}'. Cannot proceed.")
            return None
        
        # 2) 최대 30개 샘플 선정
        if len(filtered_df) <= 10:
            sample_df = filtered_df
        else:
            sample_df = filtered_df.sample(n=10, random_state=42)
        
        results_list = []
        
        for idx, row_data in sample_df.iterrows():
            original_sample = row_data.drop(labels=[target, 'predicted_class'], errors='ignore')
            logger.info(f"[Classification] Optimizing sample idx={idx}: {original_sample.to_dict()}")
            
            try:
                best_feat, best_pred, orig_pred, improvement = optimizing_features(
                    predictor=model,
                    original_features=original_sample,
                    feature_bounds=feature_bounds,
                    categorical_features=categorical_features,
                    task=task,
                    direction=direction,
                    n_trials=n_trials,
                    target_class=target_class
                )
            except Exception as e:
                logger.error(f"Optimization failed for index {idx}: {e}")
                continue

            # 변경 전후 feature 비교
            comparison_df = compare_features(original_sample, pd.Series(best_feat), categorical_features)
            logger.info(comparison_df, extra={'force': True})

            # 최종 모델 예측
            try:
                # 원본
                orig_df = pd.DataFrame([original_sample.to_dict()])
                orig_pred_class = model.predict(orig_df).iloc[0]
                
                # 최적화 후
                optimized_df = pd.DataFrame([best_feat])
                new_pred_class = model.predict(optimized_df).iloc[0]
            except Exception as e:
                logger.error(f"Prediction failed after optimization: {e}")
                continue

            logger.info(f"[Classification] Index={idx} Original pred_class={orig_pred_class}, "
                        f"Optimized pred_class={new_pred_class}, Improvement={improvement:.4f}")
            
            results_list.append({
                'index': idx,
                'original_sample': original_sample.to_dict(),
                'optimized_features': best_feat,
                'original_prediction': float(orig_pred),
                'best_prediction': float(best_pred),
                'original_pred_class': int(orig_pred_class),
                'optimized_pred_class': int(new_pred_class),
                'improvement': float(improvement),
                'comparison': comparison_df
            })

        # 3) 분류 성능 측정: 원하는 클래스(target_class)로 바뀐 개수 / 전체
        count_changed_to_target = sum(
            1 for r in results_list
            if r['optimized_pred_class'] == target_class
        )
        total_optimized = len(results_list)  # 실제 최적화가 성공적으로 끝난 샘플 수
        ratio = count_changed_to_target / total_optimized if total_optimized > 0 else 0.0
        
        logger.info(f"[Classification] 총 {total_optimized}개 중 {count_changed_to_target}개가 '{target_class}' 클래스로 변경되었습니다. (비율: {ratio:.2%})")
        
        final_dict = {
            'task': 'classification',
            'target_class': target_class,
            'results': results_list,
            'count_changed_to_target': count_changed_to_target,
            'ratio_changed_to_target': ratio
        }

        update_config(user_config_path, final_dict)
        
        return final_dict
    

# 해당 함수를 만약 사용하면 utils로 옮겨 주세요.
# numpy.int64 → Python int 변환 함수
def convert_to_serializable(obj):
    if isinstance(obj, np.integer):  # numpy int 타입 확인
        return int(obj)
    elif isinstance(obj, np.floating):  # numpy float 타입 확인 (예방용)
        return float(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")