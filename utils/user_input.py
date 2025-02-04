# import yaml
# import json
# import os

# def create_config_from_input():
#     """
#     사용자가 터미널에 입력한 값을 기반으로 설정 정보를 구성하여
#     파일에 저장한 후 그 설정 딕셔너리를 반환합니다.
#     """
#     config = {}

#     # 사용자 이름과 이메일 입력 받기
#     print(f'======= 현재는 로그인 화면입니다 =======')
#     config["user_name"] = input("사용자 이름을 입력하세요: ")
#     config["user_email"] = input("사용자 이메일을 입력하세요: ")
#     print(f'======= 현재는 데이터 업로드하는 화면입니다. =======')
#     config["data_path"] = input("데이터 파일 경로를 입력하세요: ")


#     print(f'======= 현재는 환경변수, 제어변수, 타겟변수, feature limit을 설정하는 화면입니다 =======')
#     config["target"] = input("타깃 컬럼 이름을 입력하세요: ")
#     '''
#         여기서 사용자로 부터 받는 클래스의 값이 숫자,문자 인지를 구분해야할것 같다.
#     '''
#     config["target_class"] = int(input("target_class를 입력하세요 (예: desired_class): "))
#     features = input("최적화에서 제외할 피처들을 콤마로 구분하여 입력하세요 : ")
#     config["user_fixed_features"] = [feat.strip() for feat in features.split(",") if feat.strip()]




#     # 미리 정해진 quality_map
#     config["quality_map"] = {
#         "0": "best_quality",
#         "1": "high_quality",
#         "2": "good_quality",
#         "3": "medium_quality"
#     }
#     selected_quality = input("selected_quality를 입력하세요 (0, 1, 2, 3 중 하나): ")
#     if selected_quality not in ["0", "1", "2", "3"]:
#         print("잘못된 값이 입력되어 기본값 0으로 설정합니다.")
#         config["selected_quality"] = 0
#     else:
#         config["selected_quality"] = int(selected_quality)


#     config["time_to_train"] = int(input("모델 학습 제한 시간(초)을 입력하세요: "))
#     config["n_trials"] = int(input("최적화 시도 횟수를 입력하세요: "))
#     config["direction"] = input("최적화 방향을 입력하세요 (minimize/maximize): ")




#     # 사용자가 입력한 파일명으로 저장할 것이므로, base_config_path는 사용자 입력 파일명을 사용합니다.
#     config_filename = input("설정 파일을 저장할 파일명을 입력하세요 (예: config.yaml 또는 config.json): ")

#     # 기본 저장 폴더 (절대 경로가 아닌 경우 기본 폴더를 붙임)
#     default_config_folder = "/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-22-lv3/config"
#     if not os.path.isabs(config_filename):
#         config_filename = os.path.join(default_config_folder, config_filename)

#     # base_config_path 항목에 사용자가 입력한 파일명을 그대로 사용
#     config["base_config_path"] = config_filename

#     # 파일 확장자에 따라 YAML 또는 JSON으로 저장
#     _, ext = os.path.splitext(config_filename)
#     if ext.lower() in ['.yaml', '.yml']:
#         with open(config_filename, "w", encoding="utf-8") as f:
#             yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
#     elif ext.lower() == '.json':
#         with open(config_filename, "w", encoding="utf-8") as f:
#             json.dump(config, f, indent=4, ensure_ascii=False)
#     else:
#         # 기본적으로 YAML로 저장
#         with open(config_filename, "w", encoding="utf-8") as f:
#             yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

#     print(f"설정 파일이 성공적으로 저장되었습니다: {config_filename}")
#     return config, config_filename

# if __name__ == "__main__":
#     config, config_filename = create_config_from_input()
#     print("생성된 설정:")
#     print(json.dumps(config, indent=4, ensure_ascii=False))



import yaml
import json
import os


def save_config_to_json(user_name, user_email, data_path, controllable_feature, necessary_feature, target_feature, limited_feature):
    """
    사용자의 설정 값을 JSON 파일로 저장하거나 기존 파일을 업데이트하는 함수.

    Args:
        user_name (str): 사용자 이름
        user_email (str): 사용자 이메일
        data_path (str): 데이터 파일 경로
        controllable_feature (list): 조정 가능한 피처 목록
        necessary_feature (list): 반드시 포함해야 하는 피처 목록
        target_feature (str): 예측 대상 변수
        limited_feature (int): 최대 사용할 Feature 개수

    Returns:
        str: 저장된 JSON 파일 경로
    """

    # 저장할 폴더 경로 설정
    save_dir = "/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-22-lv3/ydata_profiling"
    os.makedirs(save_dir, exist_ok=True)  # 폴더가 없으면 생성

    # 저장할 파일명 생성
    filename = f"{user_name}_{user_email}_config.json"
    file_path = os.path.join(save_dir, filename)

    # 기존 JSON 파일이 존재하면 불러와서 업데이트
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            existing_config = json.load(f)
    else:
        existing_config = {}

    # 새로운 값 추가 또는 기존 값 업데이트
    existing_config.update({
        "user_name": user_name,
        "user_email": user_email,
        "data_path": data_path,
        "controllable_feature": controllable_feature,
        "necessary_feature": necessary_feature,
        "target_feature": target_feature,
        "limited_feature": limited_feature
    })

    # 업데이트된 설정을 JSON으로 저장
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(existing_config, f, indent=4, ensure_ascii=False)

    print(f"✅ 설정 파일이 저장(또는 업데이트)되었습니다: {file_path}")
    return file_path