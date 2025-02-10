import os
import json
import openai

def gpt_solution(final_dict, model_config_path):
    """
    전달된 final_dict의 내용을 확인하고 적절히 값을 출력합니다.
    classification 결과의 경우, 각 샘플별로 controllable_feature에 해당하는
    Original Sample과 Optimized Features를 리스트에 담고, 
    각 피처별 변화량(수치형 피처)의 평균 및 상대 변화율(%)도 계산합니다.
    최종적으로, Prescriptive AI 접근법을 이용한 GPT 솔루션(response.choices[0].message.content)과 함께
    이 결과들을 포함한 JSON을 반환합니다.
    """
    from collections import defaultdict

    if isinstance(final_dict, str) and os.path.exists(final_dict):
        with open(final_dict, 'r') as f:
            final_dict = json.load(f)
            
    # 먼저 어떤 task인지 확인
    task_type = final_dict.get('task', None)
    if task_type is None:
        print("[ERROR] final_dict 안에 'task' 키가 없습니다.")
        return

    print(f"=== gpt_solution: Task = {task_type} ===")

    # model_config_path 파일에서 controllable_feature 리스트 로드 (예: ["MonthlyIncome", "WorkLifeBalance"])
    try:
        with open(model_config_path, 'r') as f:
            config = json.load(f)
        controllable_features = config.get("controllable_feature", [])
        print("Controllable features:", controllable_features)
    except Exception as e:
        print(f"[ERROR] Failed to load config from {model_config_path}: {e}")
        controllable_features = []

    # 1) 회귀(regression)인 경우
    if task_type == 'regression':
        avg_improvement = final_dict.get('average_improvement', None)
        print(f"Average improvement: {avg_improvement}")

        results = final_dict.get('results', [])
        print(f"Number of results: {len(results)}")

        for idx, item in enumerate(results):
            print(f"\n--- [Regression] Result {idx+1} ---")
            if 'error' in item:
                print(f"[ERROR] index={item['index']} / error={item['error']}")
                continue

            print(f"Index: {item['index']}")
            print(f"Original prediction: {item['original_prediction']}")
            print(f"Optimized prediction: {item['optimized_prediction']}")
            print(f"Improvement: {item['improvement']}")
            print(f"Final prediction: {item['final_prediction']}")

            comparison = item.get('comparison_df', None)
            if comparison is not None:
                print("Feature Comparison:")
                print(comparison)
        
        # 회귀의 경우엔 별도 JSON 반환 형식이 없으므로 None 반환 (또는 별도 구현)
        return None

    # 2) 분류(classification)인 경우
    elif task_type == 'classification':
        target_class = final_dict.get('target_class', None)
        optimization_direction = final_dict.get('optimization_direction', 'maximize')
        
        print(f"Target class: {target_class}")

        count_changed_to_target = final_dict.get('count_changed_to_target', 0)
        ratio_changed_to_target = final_dict.get('ratio_changed_to_target', 0.0)
        print(f"Count changed to target: {count_changed_to_target}")
        print(f"Ratio changed to target: {ratio_changed_to_target:.2%}")

        results = final_dict.get('results', [])
        print(f"Number of results: {len(results)}")

        # 리스트에 controllable_features만 담은 각 샘플 정보를 저장
        filtered_samples = []

        # 각 피처별 변화량을 계산하기 위한 딕셔너리
        feature_diff_map = defaultdict(list)

        for idx, item in enumerate(results):
            print(f"\n--- [Classification] Result {idx+1} ---")
            print(f"Index: {item['index']}")

            original_sample = item.get('original_sample', {})
            optimized_features = item.get('optimized_features', {})

            # controllable_features에 해당하는 항목만 필터링
            if controllable_features:
                filtered_original = {feat: val for feat, val in original_sample.items() if feat in controllable_features}
                filtered_optimized = {feat: val for feat, val in optimized_features.items() if feat in controllable_features}
            else:
                filtered_original = original_sample
                filtered_optimized = optimized_features

            # 리스트에 저장 (예: { "index": 1289, "original_sample": {...}, "optimized_features": {...} })
            filtered_samples.append({
                "index": item.get("index"),
                "original_sample": filtered_original,
                "optimized_features": filtered_optimized
            })

            print("Original Sample Features (filtered):")
            print(filtered_original)
            print("Optimized Features (filtered):")
            print(filtered_optimized)

            print("Original Prediction:", item.get('original_prediction', None))
            print("Best(Optimized) Prediction:", item.get('best_prediction', None))
            print("Original Predicted Class:", item.get('original_pred_class', None))
            print("Optimized Predicted Class:", item.get('optimized_pred_class', None))
            print("Improvement:", item.get('improvement', None))

            # (2) 변화량 수집 (수치형 피처만 처리) - 필터링된 값 사용
            for feat in filtered_original.keys():
                if feat in filtered_optimized:
                    orig_val = filtered_original[feat]
                    opt_val = filtered_optimized[feat]

                    if isinstance(orig_val, (int, float)) and isinstance(opt_val, (int, float)):
                        abs_change = opt_val - orig_val
                        ratio_change = (abs_change / orig_val) * 100.0 if abs(orig_val) > 1e-12 else None
                        feature_diff_map[feat].append((abs_change, ratio_change))

        # (3) 모든 샘플 처리 후, 각 피처별 평균 변화량 및 평균 상대 변화율 계산
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

        # API 키 설정 (환경 변수 또는 .env 파일 등을 사용)
        openai.api_key = os.getenv("OPENAI_API_KEY", '')
        if openai.api_key is None:
            raise ValueError("OPENAI_API_KEY 환경 변수가 설정되어 있지 않습니다!")

        # GPT에게 보낼 메시지 내용 구성
        user_message = (
            "Based on the following feature change analysis and final results, our overall goal is to optimize the feature value for the target class for the prediction probability "
            f"for the target class (value: {target_class}) by optimizing the feature value in the direction of '{optimization_direction}' direction. \n\n"
            "Use a prescriptive AI approach to provide detailed, actionable recommendations on how to modify features to improve the model's predictions. "
            "Consider the average absolute and relative change for each feature and provide clear insights into which features should be prioritized. \n\n"
            "For example, a 5% increase in monthly revenue typically leads to higher employee satisfaction and consequently lower turnover. "
            "However, the analysis shows that changes in WorkLifeBalance are not significant in the model's predictions, suggesting that this feature may have a small impact on turnover. \n\n"
            "Please provide a detailed feature analysis and any strategic recommendations for the company or organization. "
            "Please provide specific examples of overall strategies, such as HR initiatives, financial incentive programs, or workplace improvements, that can help us achieve these optimization goals. "
            "For example, you might recommend implementing performance-based bonuses to increase monthly income or launching an employee engagement program to further reduce turnover. \n\n"
            "Please create comprehensive, easy-to-understand recommendations that combine both technical insights and high-level strategic guidance. \n\n"
            f"{analysis_text}. Please write your answer in Korean and do not analyze data with zero change."
        )

        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert data analyst and machine learning consultant with prescriptive AI expertise."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            temperature=0.5,
            max_tokens=2500
        )

        gpt_response_text = response.choices[0].message.content
        print("\n=== GPT API Response ===")
        print(gpt_response_text)

        # 최종적으로 samples와 GPT 솔루션을 포함하는 JSON 객체 생성
        output_data = {
            "samples": filtered_samples,
            "solution": gpt_response_text
        }

        # JSON 문자열로 반환 (indent 및 ensure_ascii 옵션 사용)
        return json.dumps(output_data, indent=4, ensure_ascii=False)

    else:
        print("[ERROR] 알 수 없는 task입니다.")
        return None