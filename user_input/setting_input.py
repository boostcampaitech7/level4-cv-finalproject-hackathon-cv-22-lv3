def user_base_setting(all_features, numeric_key_features):
    """
    Prompt the user for basic optimization settings.

    Parameters
        all_features : list
            List of all features.
        numeric_key_features : list
            List of numeric features for optimization.

    Returns
        dict
            Dictionary containing:
                - 'target_feature': Feature to predict.
                - 'controllable_feature': List of features to optimize.
                - 'necessary_feature': List of features for training.
                - 'limited_feature': Maximum number of features to use.
    """
    print("\n\n ======= 기본 세팅값 화면 =======")
    print(f"Target Feature 리스트:\n {all_features}\n")
    target_feature = input("최종적으로 예측하고자 하는 변수를 입력해주세요. (기본값: Attrition) : ")
    if target_feature == "":
        target_feature = "Attrition"

    print(f"조절 가능한 Feature들:\n {numeric_key_features}")
    controllable_feature = input("\n\n최적화에 사용될 조절 가능한 변수를 설정해주세요. (쉼표로 구분, 기본값: 전체) : ")
    if controllable_feature.strip() == "":
        controllable_feature = []
    else:
        controllable_feature = [feat.strip() for feat in controllable_feature.split(",") if feat.strip()]

    print(f"조절 불가능한 Feature들:\n {all_features}")
    necessary_feature = input("\n훈련에 사용될 조절 불가능한 변수를 설정해주세요. (쉼표로 구분, 기본값: 전체) : ")
    if necessary_feature.strip() == "":
        necessary_feature = []
    else:
        necessary_feature = [feat.strip() for feat in necessary_feature.split(",") if feat.strip()]

    try:
        limited_feature = int(input("모델 학습 시 최대로 사용할 Feature의 수를 설정해주세요 (기본값 : 50 ) : ") or -1)
    except ValueError:
        print("숫자가 입력되지 않아 모든 Feature를 학습으로 설정됩니다.")
        limited_feature = -1

    user_settings = {
        "target_feature": target_feature,
        "controllable_feature": controllable_feature,
        "necessary_feature": necessary_feature,
        "limited_feature": limited_feature,
    }
    return user_settings


def model_base_setting(task):
    """
    Prompt the user for model settings.

    Parameters
        task : str
            The prediction task type.

    Returns
        dict
            Dictionary with model settings:
                {'model': {'task': task, 'time_to_train': int, 'model_quality': int}}
    """
    print("\n\n ======= 모델 세팅 화면 =======")
    model_quality = int(input(
        """모델의 퀄리티를 설정해주세요  
"0": best_quality
"1": high_quality
"2": good_quality
"3": medium_quality
[answer]: """
    ))
    time_to_train = int(input("학습할 시간을 설정해주세요 (초): "))
    return {"model": {"task": task, "time_to_train": time_to_train, "model_quality": model_quality}}


def base_optimize_setting(config):
    """
    Prompt the user for optimization settings.

    Parameters
    ----------
    config : dict
        Configuration dictionary containing:
            - 'model': dict with key 'task'
            - 'controllable_feature': list of features to optimize
            - 'filtered_result': dict with feature statistics

    Returns
    -------
    dict
        Dictionary with optimization settings:
            {'optimization': {'direction': str,
                              'n_trials': int,
                              'target_class': int or None,
                              'opt_range': dict}}
    """
    print("\n\n ======= 최적화 세팅 화면 =======")
    task = config["model"].get("task")
    controllable_feature = config["controllable_feature"]
    statistics = config["filtered_result"]
    opt_range = {}
    for f in controllable_feature:
        f_info = statistics[f]
        if f_info["type"] == "Numeric":
            print(f'{f}의 범위: ({f_info["min"]}, {f_info["max"]})')
            min_max = input(
                f'{f}의 제어가능한 범위를 설정하기 위해 최소값, 최대값 순으로 입력해주세요. (쉼표로 구분, 기본값: 전체 값에 대한 min, max) : '
            )
            if not min_max.strip():
                opt_range[f] = [f_info["min"], f_info["max"]]
            else:
                range_vals = [int(mm.strip()) for mm in min_max.split(",") if mm.strip()]
                if len(range_vals) != 2:
                    print(f"입력 형식이 올바르지 않습니다. 기본값 ({f_info['min']}, {f_info['max']})을 사용합니다.")
                    opt_range[f] = [f_info["min"], f_info["max"]]
                else:
                    if range_vals[0] > range_vals[1]:
                        print(f"입력한 최소값({range_vals[0]})이 최대값({range_vals[1]})보다 큽니다. 값을 서로 교환합니다.")
                        range_vals = [range_vals[1], range_vals[0]]
                    opt_range[f] = range_vals
        else:
            _range = [0, f_info["n_distinct"] - 1]
            opt_range[f] = _range
            print(f'{f}의 제어가능한 범위: ({_range[0]}, {_range[1]})')

    if task != "regression":
        target_class = int(input("최적화하고 싶은 Feature의 클래스를 선택해주세요 : "))
        direction = "maximize"
    else:
        target_class = None
        while True:
            direction = input("Target Feature를 최소/최대화할지 고르세요 (minimize | maximize) : ").strip().lower()
            if direction in ["minimize", "maximize"]:
                break
            else:
                print("잘못된 입력입니다. 'minimize' 또는 'maximize'를 입력해주세요.")
    n_trials = int(input("최적화를 시도할 횟수를 선택하세요 : "))
    return {
        "optimization": {
            "direction": direction,
            "n_trials": n_trials,
            "target_class": target_class,
            "opt_range": opt_range,
        }
    }