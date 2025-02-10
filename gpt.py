import os
import json
import openai

from omegaconf import OmegaConf
from collections import defaultdict
from config.update_config import update_config

def gpt_solution(final_dict, model_config_path, user_config_path):
    """
    전달된 final_dict의 내용을 확인하고 적절히 값을 출력 및 분석한 후,
    controllable feature들을 조정하여 target feature를 원하는 방향으로 변경할 수 있는
    구체적 실행 전략에 대해 GPT 솔루션(response.choices[0].message.content)을 포함한 JSON을 반환합니다.
    """

    
    model_config = OmegaConf.load(model_config_path)
    user_config = OmegaConf.load(user_config_path)
    task_type = user_config.get("task")
    
            
    # task 타입 확인
    task_type = final_dict.get('task', None)
    if task_type is None:
        print("[ERROR] final_dict 안에 'task' 키가 없습니다.")
        return

    print(f"=== gpt_solution: Task = {task_type} ===")

    # model_config_path에서 controllable_feature 리스트 로드
    try:
        controllable_features = model_config.get("controllable_feature", [])
        print("Controllable features:", controllable_features)
    except Exception as e:
        print(f"[ERROR] Failed to load config from {model_config_path}: {e}")
        controllable_features = []


    openai.api_key = os.getenv("OPENAI_API_KEY", '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')
    if openai.api_key is None:
        raise ValueError("OPENAI_API_KEY 환경 변수가 설정되어 있지 않습니다!")


    # 1) 회귀 (regression)인 경우
    if task_type == 'regression':
        avg_improvement = final_dict.get('average_improvement', None)
        print(f"Average improvement: {avg_improvement}")

        results = final_dict.get('results', [])
        print(f"Number of results: {len(results)}")

        direction = config.get('optimization', {}).get('direction', None)
        target_feature = config.get('target_feature', None)
        print(f'direction = {direction}')
        print(f'target_feature = {target_feature}')

        # regression 결과에 대한 샘플 정보와 controllable feature의 변화량을 저장할 변수들
        filtered_samples = []
        feature_diff_map = defaultdict(list)

        for idx, item in enumerate(results):
            print(f"\n--- [Regression] Result {idx+1} ---")
            if 'error' in item:
                print(f"[ERROR] index={item.get('index')} / error={item.get('error')}")
                continue

            print(f"Index: {item.get('index')}")
            print(f"Original prediction: {item.get('original_prediction')}")
            print(f"Optimized prediction: {item.get('optimized_prediction')}")
            print(f"Improvement: {item.get('improvement')}")
            print(f"Final prediction: {item.get('final_prediction')}")

            # comparison_df가 controllable feature의 변화 내용을 포함하는 경우
            comparison = item.get('comparison_df', None)
            if comparison is not None:
                print("Feature Comparison:")
                print(comparison)
                
                # 만약 comparison이 dict 형태라면 controllable feature별로 변화량을 추출
                if isinstance(comparison, dict):
                    for feat in controllable_features:
                        if feat in comparison:
                            # comparison[feat]가 "원래값 -> 최적화값" 형태의 문자열이라고 가정
                            try:
                                parts = comparison[feat].split("->")
                                if len(parts) == 2:
                                    orig_val = float(parts[0].strip())
                                    opt_val = float(parts[1].strip())
                                    abs_change = opt_val - orig_val
                                    ratio_change = (abs_change / orig_val * 100.0) if abs(orig_val) > 1e-12 else None
                                    feature_diff_map[feat].append((abs_change, ratio_change))
                            except Exception as e:
                                print(f"[WARN] 비교값 파싱 실패 for feature '{feat}': {e}")

            # 결과 정보를 샘플로 저장 (추후 GPT에 전달할 정보)
            filtered_samples.append({
                "index": item.get("index"),
                "original_prediction": item.get("original_prediction"),
                "optimized_prediction": item.get("optimized_prediction"),
                "final_prediction": item.get("final_prediction"),
                "comparison": comparison
            })

        # controllable feature별 평균 변화량 및 상대 변화율 계산
        analysis_text = "\n=== [Regression] 피처별 변화량 분석 ===\n"
        for feat, diff_list in feature_diff_map.items():
            if not diff_list:
                continue
            abs_change_list = [d[0] for d in diff_list if d[0] is not None]
            ratio_list = [d[1] for d in diff_list if d[1] is not None]
            avg_abs_change = sum(abs_change_list) / len(abs_change_list) if abs_change_list else 0.0
            avg_ratio = sum(ratio_list) / len(ratio_list) if ratio_list else 0.0
            analysis_text += f"Feature: {feat}\n"
            analysis_text += f"  - Average Absolute Change: {avg_abs_change:.4f}\n"
            analysis_text += f"  - Average Relative Change: {avg_ratio:.4f}% (기준=original)\n"

        print(analysis_text)

        # GPT에게 보낼 메시지 구성
        # (참고: regression에서는 최적화 방향이 별도로 주어지지 않으므로, 분석 결과를 토대로
        #  controllable feature들을 어떻게 조정하면 타겟 예측값이 원하는 방향으로 변화할 수 있을지 전략을 요청)

        user_message = (
            "Based on the following regression model feature change analysis, each result demonstrates how changes in controllable features affect the predicted value. "
            f"Our objective is to adjust the controllable features so that the target feature '{target_feature}' is optimized in the '{direction}' direction. \n\n"
            "Using a prescriptive AI approach, please provide detailed, actionable recommendations on how to modify the values of the controllable features (e.g., " 
            + ", ".join(controllable_features) +
            ") to achieve the desired outcome for the target feature. "
            "Consider the average absolute and relative changes for each feature as provided below, and offer clear insights into which features should be prioritized. \n\n"
            "For example, a 5% increase in a key metric might lead to significant improvements, while adjustments in another feature might have a minimal impact. \n\n"
            "Please provide specific examples of overall strategies, such as marketing initiatives, cost reduction measures, or process improvements, that could help achieve these optimization goals. \n\n"
            f"Here is the feature change analysis:\n{analysis_text}\n\n"
            "And make the analysis a little more numerical and logical."
            "Please write your answer in korean and exclude any analysis for features with zero change."
        )

        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert data analyst and machine learning consultant with prescriptive AI expertise."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.5,
            max_tokens=2500
        )

        gpt_response_text = response.choices[0].message.content
        print("\n=== GPT API Response ===")
        print(gpt_response_text)

        # 최종적으로 샘플 정보와 GPT 솔루션을 포함하는 JSON 객체 생성
        output_data = {
            "samples": filtered_samples,
            "solution": gpt_response_text
        }

        return json.dumps(output_data, indent=4, ensure_ascii=False, default=convert_to_serializable)

    # 2) 분류 (classification)인 경우는 기존 코드 사용
    elif task_type == 'classification':
        optimization_direction = config.get('optimization', {}).get('direction', None)
        target_class = config.get('optimization', {}).get('target_class', None)

        
        print(f"Target class: {target_class}")

        count_changed_to_target = final_dict.get('count_changed_to_target', 0)
        ratio_changed_to_target = final_dict.get('ratio_changed_to_target', 0.0)
        print(f"Count changed to target: {count_changed_to_target}")
        print(f"Ratio changed to target: {ratio_changed_to_target:.2%}")

        results = final_dict.get('results', [])
        print(f"Number of results: {len(results)}")


        filtered_samples = []
        feature_diff_map = defaultdict(list)

        for idx, item in enumerate(results):
            print(f"\n--- [Classification] Result {idx+1} ---")
            print(f"Index: {item.get('index')}")
            original_sample = item.get('original_sample', {})
            optimized_features = item.get('optimized_features', {})

            if controllable_features:
                filtered_original = {feat: val for feat, val in original_sample.items() if feat in controllable_features}
                filtered_optimized = {feat: val for feat, val in optimized_features.items() if feat in controllable_features}
            else:
                filtered_original = original_sample
                filtered_optimized = optimized_features

            filtered_samples.append({
                "index": item.get("index"),
                "original_sample": filtered_original,
                "optimized_features": filtered_optimized
            })

            print("Original Sample Features (filtered):")
            print(filtered_original)
            print("Optimized Features (filtered):")
            print(filtered_optimized)

            print("Original Prediction:", item.get('original_prediction'))
            print("Best(Optimized) Prediction:", item.get('best_prediction'))
            print("Original Predicted Class:", item.get('original_pred_class'))
            print("Optimized Predicted Class:", item.get('optimized_pred_class'))
            print("Improvement:", item.get('improvement'))

            for feat in filtered_original.keys():
                if feat in filtered_optimized:
                    orig_val = filtered_original[feat]
                    opt_val = filtered_optimized[feat]
                    if isinstance(orig_val, (int, float)) and isinstance(opt_val, (int, float)):
                        abs_change = opt_val - orig_val
                        ratio_change = (abs_change / orig_val) * 100.0 if abs(orig_val) > 1e-12 else None
                        feature_diff_map[feat].append((abs_change, ratio_change))

        print("\n=== [Classification] 피처별 변화량 분석 ===")
        analysis_text = "\n=== [Classification] 피처별 변화량 분석 ===\n"
        for feat, diff_list in feature_diff_map.items():
            if not diff_list:
                continue
            abs_change_list = [d[0] for d in diff_list if d[0] is not None]
            ratio_list = [d[1] for d in diff_list if d[1] is not None]
            avg_abs_change = sum(abs_change_list) / len(abs_change_list) if abs_change_list else 0.0
            avg_ratio = sum(ratio_list) / len(ratio_list) if ratio_list else 0.0
            analysis_text += f"Feature: {feat}\n"
            analysis_text += f"  - Average Absolute Change: {avg_abs_change:.4f}\n"
            analysis_text += f"  - Average Relative Change: {avg_ratio:.4f}% (기준=original)\n"

        print(analysis_text)


        user_message = (
            f"start say with Our model optimization results in a {ratio_changed_to_target} ratio to our desired target."
            "Based on the following feature change analysis and final results, our overall goal is to optimize the feature value for the target class "
            f"(value: {target_class}) by optimizing the feature value in the direction of '{optimization_direction}' direction. \n\n"
            "Use a prescriptive AI approach to provide detailed, actionable recommendations on how to modify features to improve the model's predictions. "
            "Consider the average absolute and relative change for each feature and provide clear insights into which features should be prioritized. \n\n"
            "For example, a 5% increase in monthly revenue typically leads to higher employee satisfaction and consequently lower turnover. "
            "And make the analysis a little more numerical and logical."
            "However, the analysis shows that changes in WorkLifeBalance are not significant in the model's predictions, suggesting that this feature may have a small impact on turnover. \n\n"
            "Please provide a detailed feature analysis and any strategic recommendations for the company or organization. "
            "Please provide specific examples of overall strategies, such as HR initiatives, financial incentive programs, or workplace improvements, that can help us achieve these optimization goals. \n\n"
            "Please create comprehensive, easy-to-understand recommendations that combine both technical insights and high-level strategic guidance. \n\n"
            f"{analysis_text}. Please write your answer in Korean and do not analyze data with zero change."
        )

        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert data analyst and machine learning consultant with prescriptive AI expertise."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.5,
            max_tokens=2500
        )

        gpt_response_text = response.choices[0].message.content
        print("\n=== GPT API Response ===")
        print(gpt_response_text)

        output_data = {
            "samples": filtered_samples,
            "solution": gpt_response_text
        }


        # JSON 문자열로 반환 (indent 및 ensure_ascii 옵션 사용)
        update_config(user_config_path, output_data)
        return user_config_path

    else:
        print("[ERROR] 알 수 없는 task입니다.")
        return None