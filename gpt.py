import os
import json
import openai
from collections import defaultdict
from omegaconf import OmegaConf
from config.update_config import update_config
from optimization.feature_optimization import convert_to_serializable  # noqa: F401


def gpt_solution(final_dict, model_config_path, user_config_path):
    """
    Generate a GPT-based solution based on optimization results.

    This function examines the final_dict from the optimization process,
    analyzes the changes in controllable features, and uses the GPT API
    to provide actionable recommendations to adjust these features in order
    to optimize the target feature. The GPT solution is saved to the user
    configuration file.

    Parameters
        final_dict : dict
            Dictionary containing the optimization results.
        model_config_path : str
            Path to the model configuration file.
        user_config_path : str
            Path to the user configuration file.

    Returns
        str or None
            The updated user configuration file path containing the GPT solution,
            or None if the task type is unknown.
    """
    model_config = OmegaConf.load(model_config_path)
    user_config = OmegaConf.load(user_config_path)
    task_type = final_dict.get("task", None)
    if task_type is None:
        print("[ERROR] 'task' key is missing in final_dict.")
        return

    print(f"=== gpt_solution: Task = {task_type} ===")

    try:
        controllable_features = model_config.get("controllable_feature", [])
        print("Controllable features:", controllable_features)
    except Exception as e:
        print(f"[ERROR] Failed to load config from {model_config_path}: {e}")
        controllable_features = []

    openai.api_key = os.getenv("OPENAI_API_KEY", "Enter your gpt api key")
    if openai.api_key is None:
        raise ValueError("OPENAI_API_KEY environment variable is not set!")

    if task_type == "regression":
        avg_improvement = final_dict.get("average_improvement", None)
        print(f"Average improvement: {avg_improvement}")

        results = final_dict.get("results", [])
        print(f"Number of results: {len(results)}")

        direction = model_config.get("optimization", {}).get("direction", None)
        target_feature = model_config.get("target_feature", None)
        print(f"direction = {direction}")
        print(f"target_feature = {target_feature}")

        filtered_samples = []
        feature_diff_map = defaultdict(list)

        for idx, item in enumerate(results):
            print(f"\n--- [Regression] Result {idx+1} ---")
            if "error" in item:
                print(f"[ERROR] index={item.get('index')} / error={item.get('error')}")
                continue

            print(f"Index: {item.get('index')}")
            print(f"Original prediction: {item.get('original_prediction')}")
            print(f"Optimized prediction: {item.get('optimized_prediction')}")
            print(f"Improvement: {item.get('improvement')}")
            print(f"Final prediction: {item.get('final_prediction')}")

            comparison = item.get("comparison_df", None)
            if comparison is not None:
                print("Feature Comparison:")
                print(comparison)
                if isinstance(comparison, dict):
                    for feat in controllable_features:
                        if feat in comparison:
                            try:
                                parts = comparison[feat].split("->")
                                if len(parts) == 2:
                                    orig_val = float(parts[0].strip())
                                    opt_val = float(parts[1].strip())
                                    abs_change = opt_val - orig_val
                                    ratio_change = (abs_change / orig_val * 100.0
                                                    if abs(orig_val) > 1e-12 else None)
                                    feature_diff_map[feat].append((abs_change, ratio_change))
                            except Exception as e:
                                print(f"[WARN] Failed to parse change for feature '{feat}': {e}")

            filtered_samples.append({
                "index": item.get("index"),
                "original_prediction": item.get("original_prediction"),
                "optimized_prediction": item.get("optimized_prediction"),
                "final_prediction": item.get("final_prediction"),
                "comparison": comparison,
            })

        analysis_text = "\n=== [Regression] Feature Change Analysis ===\n"
        for feat, diff_list in feature_diff_map.items():
            if not diff_list:
                continue
            abs_change_list = [d[0] for d in diff_list if d[0] is not None]
            ratio_list = [d[1] for d in diff_list if d[1] is not None]
            avg_abs_change = sum(abs_change_list) / len(abs_change_list) if abs_change_list else 0.0
            avg_ratio = sum(ratio_list) / len(ratio_list) if ratio_list else 0.0
            analysis_text += f"Feature: {feat}\n"
            analysis_text += f"  - Average Absolute Change: {avg_abs_change:.4f}\n"
            analysis_text += f"  - Average Relative Change: {avg_ratio:.4f}% (based on original)\n"

        print(analysis_text)

        user_message = (
            "Don't give me an answer like '물론입니다.', just give me only a solution. "
            "Based on the following regression model feature change analysis, each result demonstrates "
            "how changes in controllable features affect the predicted value. "
            f"Our objective is to adjust the controllable features so that the target feature '{target_feature}' "
            f"is optimized in the '{direction}' direction.\n\n"
            "Using a prescriptive AI approach, please provide detailed, actionable recommendations on how to "
            "modify the values of the controllable features (e.g., " + ", ".join(controllable_features) + 
            ") to achieve the desired outcome for the target feature. Consider the average absolute and relative "
            "changes for each feature as provided below, and offer clear insights into which features should be prioritized.\n\n"
            "For example, a 5% increase in a key metric might lead to significant improvements, while adjustments in "
            "another feature might have a minimal impact.\n\n"
            "Please provide specific examples of overall strategies, such as marketing initiatives, cost reduction measures, "
            "or process improvements, that could help achieve these optimization goals.\n\n"
            f"Here is the feature change analysis:\n{analysis_text}\n\n"
            "And make the analysis a little more numerical and logical. "
            "Please write your answer in Korean and exclude any analysis for features with zero change."
        )

        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert data analyst and machine learning consultant with prescriptive AI expertise."
                    )
                },
                {"role": "user", "content": user_message},
            ],
            temperature=0.5,
            max_tokens=2500,
        )

        gpt_response_text = response.choices[0].message.content
        print("\n=== GPT API Response ===")
        print(gpt_response_text)

        output_data = {
            "samples": filtered_samples,
            "solution": gpt_response_text,
        }

        update_config(user_config_path, output_data)
        return user_config_path

    elif task_type == "classification":
        optimization_direction = model_config.get("optimization", {}).get("direction", None)
        target_class = model_config.get("optimization", {}).get("target_class", None)

        print(f"Target class: {target_class}")

        count_changed_to_target = final_dict.get("count_changed_to_target", 0)
        ratio_changed_to_target = final_dict.get("ratio_changed_to_target", 0.0)
        print(f"Count changed to target: {count_changed_to_target}")
        print(f"Ratio changed to target: {ratio_changed_to_target:.2%}")

        results = final_dict.get("results", [])
        print(f"Number of results: {len(results)}")

        filtered_samples = []
        feature_diff_map = defaultdict(list)

        for idx, item in enumerate(results):
            print(f"\n--- [Classification] Result {idx+1} ---")
            print(f"Index: {item.get('index')}")
            original_sample = item.get("original_sample", {})
            optimized_features = item.get("optimized_features", {})

            if controllable_features:
                filtered_original = {feat: val for feat, val in original_sample.items() if feat in controllable_features}
                filtered_optimized = {feat: val for feat, val in optimized_features.items() if feat in controllable_features}
            else:
                filtered_original = original_sample
                filtered_optimized = optimized_features

            filtered_samples.append({
                "index": item.get("index"),
                "original_sample": filtered_original,
                "optimized_features": filtered_optimized,
            })

            print("Original Sample Features (filtered):")
            print(filtered_original)
            print("Optimized Features (filtered):")
            print(filtered_optimized)

            print("Original Prediction:", item.get("original_prediction"))
            print("Best (Optimized) Prediction:", item.get("best_prediction"))
            print("Original Predicted Class:", item.get("original_pred_class"))
            print("Optimized Predicted Class:", item.get("optimized_pred_class"))
            print("Improvement:", item.get("improvement"))

            for feat in filtered_original.keys():
                if feat in filtered_optimized:
                    orig_val = filtered_original[feat]
                    opt_val = filtered_optimized[feat]
                    if isinstance(orig_val, (int, float)) and isinstance(opt_val, (int, float)):
                        abs_change = opt_val - orig_val
                        ratio_change = (abs_change / orig_val * 100.0) if abs(orig_val) > 1e-12 else None
                        feature_diff_map[feat].append((abs_change, ratio_change))

        analysis_text = "\n=== [Classification] Feature Change Analysis ===\n"
        for feat, diff_list in feature_diff_map.items():
            if not diff_list:
                continue
            abs_change_list = [d[0] for d in diff_list if d[0] is not None]
            ratio_list = [d[1] for d in diff_list if d[1] is not None]
            avg_abs_change = sum(abs_change_list) / len(abs_change_list) if abs_change_list else 0.0
            avg_ratio = sum(ratio_list) / len(ratio_list) if ratio_list else 0.0
            analysis_text += f"Feature: {feat}\n"
            analysis_text += f"  - Average Absolute Change: {avg_abs_change:.4f}\n"
            analysis_text += f"  - Average Relative Change: {avg_ratio:.4f}% (based on original)\n"

        print(analysis_text)

        user_message = (
            "Don't give me an answer like '물론입니다.' just give me only a solution."
            f" Start by stating that our model optimization resulted in a {ratio_changed_to_target} ratio to our desired target. "
            "Based on the following feature change analysis and final results, our overall goal is to optimize the feature value for the target class "
            f"(value: {target_class}) by adjusting the feature values in the '{optimization_direction}' direction.\n\n"
            "Using a prescriptive AI approach, provide detailed, actionable recommendations on how to modify the features to improve the model's predictions. "
            "Consider the average absolute and relative change for each feature and indicate which features should be prioritized.\n\n"
            "For example, a 5% increase in monthly revenue might lead to higher employee satisfaction and lower turnover. "
            "Note that the analysis shows that changes in WorkLifeBalance are minimal, suggesting a small impact on turnover.\n\n"
            "Please provide a detailed feature analysis along with strategic recommendations (e.g., HR initiatives, financial incentive programs, or workplace improvements) "
            "in Korean. Exclude any analysis for features with zero change.\n\n"
            f"{analysis_text}"
        )

        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert data analyst and machine learning consultant with prescriptive AI expertise."
                    ),
                },
                {"role": "user", "content": user_message},
            ],
            temperature=0.5,
            max_tokens=2500,
        )

        gpt_response_text = response.choices[0].message.content
        print("\n=== GPT API Response ===")
        print(gpt_response_text)

        output_data = {
            "samples": filtered_samples,
            "solution": gpt_response_text,
        }

        update_config(user_config_path, output_data)
        return user_config_path

    else:
        print("[ERROR] Unknown task type.")
        return None