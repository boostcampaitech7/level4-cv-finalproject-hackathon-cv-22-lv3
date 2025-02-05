import yaml
import json
import os


def user_base_setting(features):
    """
    summary: 사용자에게 최적화 설정을 입력받아 반환하는 함수

    return:
        dict: 설정된 변수들을 포함한 딕셔너리
    """
    
    print(f'\n\n ======= 현재는 기본 세팅값을 설정하는 화면입니다 =======')

    print(f'아래의 Feature들은 현재 데이터의 feature들 입니다. \n\n {features}')

    target_feature = input('최종적으로 예측하고자 하는 변수를 입력해주세요. (기본값: Attrition) : ') or "Attrition"
    
    # 쉼표로 구분된 경우 리스트로 변환
    controllable_feature = input('최적화에 사용될 조절 가능한 변수를 설정해주세요. (쉼표로 구분, 기본값: 전체) : ')
    if controllable_feature.strip() == "":
        controllable_feature = []  # 또는 원하는 기본 리스트
    else:
        controllable_feature = [feat.strip() for feat in controllable_feature.split(",") if feat.strip()]
    opt_range = {}
    for f in controllable_feature:
        min_max = input(f'{f}의 제어가능한 범위를 설정하기 위해 최소값, 최대값 순으로 입력해주세요. (쉼표로 구분, 기본값: 전체 값에 대한 min, max) : ')
        opt_range[f] = [int(mm.strip()) for mm in min_max.split(",") if mm.strip()]
        
    necessary_feature = input('훈련에 사용될 조절 불가능한 변수를 설정해주세요. (쉼표로 구분, 기본값: 전체) : ')

    if necessary_feature.strip() == "":
        necessary_feature = []  # 또는 원하는 기본 리스트
    else:
        necessary_feature = [feat.strip() for feat in necessary_feature.split(",") if feat.strip()]
        

    # 숫자 입력 오류 방지를 위한 예외 처리 (입력하지 않으면 기본값 50 사용)
    try:
        limited_feature = int(input('모델 학습 시 최대로 사용할 Feature의 수를 설정해주세요 (기본값 : 50 ) : ') or -1)
    except ValueError:
        print("숫자가 입력되지 않아 모든 Feature를 학습으로 설정됩니다.")
        limited_feature = -1

    # 결과를 딕셔너리로 반환
    user_settings = {
        "target_feature": target_feature,
        "controllable_feature": controllable_feature,
        "opt_range": opt_range,
        "necessary_feature": necessary_feature,
        "limited_feature": limited_feature
    }

    return user_settings


def model_base_setting(task):
    """
    모델 세팅을 입력받고 설정값을 딕셔너리로 반환하는 함수.

    Returns:
        dict: {'model': {'time_to_train': int, 'model_quality': int}}
    """
    print(f'\n\n ======= 현재는 모델 세팅 화면 입니다. =======')

    model_quality = int(input(
        """모델의 퀄리티를 설정해주세요  
        "0": "best_quality"
        "1": "high_quality"
        "2": "good_quality"
        "3": "medium_quality"
        [answer]: """
    ))

    time_to_train = int(input("학습할 시간을 설정해주세요 (초): "))

    return {"model": {"task": task, "time_to_train": time_to_train, "model_quality": model_quality}}


def base_optimize_setting(task):
    """
    최적화 세팅을 입력받고 설정값을 딕셔너리로 반환하는 함수.

    Args:
        merged_file_path (str): 병합된 데이터 파일 경로
        task (str): "regression" 또는 classification 관련 작업 유형

    Returns:
        dict: {'optimization': {'direction': str, 'n_trials': int, 'target_class': str or None}}
    """
    print('\n\n ======= 현재는 최적화 세팅 화면 입니다. =======')

    if task != 'regression':
        target_class = int(input('최적화하고 싶은 Feature의 클래스를 선택해주세요 : '))
        direction = 'maximize'
    else:
        target_class = None
        while True:
            direction = input('Target Feature를 최소/최대화할지 고르세요 (minimize | maximize) : ').strip().lower()
            if direction in ['minimize', 'maximize']:
                break
            else:
                print("잘못된 입력입니다. 'minimize' 또는 'maximize'를 입력해주세요.")
    
    n_trials = int(input('최적화를 시도할 횟수를 선택하세요 : '))

    return {"optimization": {"direction": direction, "n_trials": n_trials, "target_class": target_class}}