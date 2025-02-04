import yaml
import json
import os

def create_config_from_input():
    """
    사용자가 터미널에 입력한 값을 기반으로 설정 정보를 구성하여
    파일에 저장한 후 그 설정 딕셔너리를 반환합니다.
    """
    config = {}

    # 사용자 이름과 이메일 입력 받기
    config["user_name"] = input("사용자 이름을 입력하세요: ")
    config["user_email"] = input("사용자 이메일을 입력하세요: ")

    config["data_path"] = input("데이터 파일 경로를 입력하세요: ")
    config["target"] = input("타깃 컬럼 이름을 입력하세요: ")

    # 미리 정해진 quality_map
    config["quality_map"] = {
        "0": "best_quality",
        "1": "high_quality",
        "2": "good_quality",
        "3": "medium_quality"
    }

    # selected_quality 입력 받기 (0, 1, 2, 3 중 선택)
    selected_quality = input("selected_quality를 입력하세요 (0, 1, 2, 3 중 하나): ")
    if selected_quality not in ["0", "1", "2", "3"]:
        print("잘못된 값이 입력되어 기본값 0으로 설정합니다.")
        config["selected_quality"] = 0
    else:
        config["selected_quality"] = int(selected_quality)

    config["time_to_train"] = int(input("모델 학습 제한 시간(초)을 입력하세요: "))
    config["n_trials"] = int(input("최적화 시도 횟수를 입력하세요: "))
    config["direction"] = input("최적화 방향을 입력하세요 (minimize/maximize): ")


    '''
        여기서 사용자로 부터 받는 클래스의 값이 숫자,문자 인지를 구분해야할것 같다.
    '''
    config["target_class"] = int(input("target_class를 입력하세요 (예: desired_class): "))
    # config["threshold"] = int(input("threshold 값을 입력하세요: "))

    # 고정 피처 목록 (콤마로 구분하여 입력)
    features = input("최적화에서 제외할 피처들을 콤마로 구분하여 입력하세요 (예: age, sex, G1, G2, absences): ")
    config["user_fixed_features"] = [feat.strip() for feat in features.split(",") if feat.strip()]


    # 사용자가 입력한 파일명으로 저장할 것이므로, base_config_path는 사용자 입력 파일명을 사용합니다.
    config_filename = input("설정 파일을 저장할 파일명을 입력하세요 (예: config.yaml 또는 config.json): ")

    # 기본 저장 폴더 (절대 경로가 아닌 경우 기본 폴더를 붙임)
    default_config_folder = "/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-22-lv3/config"
    if not os.path.isabs(config_filename):
        config_filename = os.path.join(default_config_folder, config_filename)

    # base_config_path 항목에 사용자가 입력한 파일명을 그대로 사용
    config["base_config_path"] = config_filename

    # 파일 확장자에 따라 YAML 또는 JSON으로 저장
    _, ext = os.path.splitext(config_filename)
    if ext.lower() in ['.yaml', '.yml']:
        with open(config_filename, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    elif ext.lower() == '.json':
        with open(config_filename, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    else:
        # 기본적으로 YAML로 저장
        with open(config_filename, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    print(f"설정 파일이 성공적으로 저장되었습니다: {config_filename}")
    return config, config_filename

if __name__ == "__main__":
    config, config_filename = create_config_from_input()
    print("생성된 설정:")
    print(json.dumps(config, indent=4, ensure_ascii=False))