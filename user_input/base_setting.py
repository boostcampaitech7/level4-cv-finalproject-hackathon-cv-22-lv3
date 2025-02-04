import yaml
import json
import os

def user_base_setting(features):
    """
    summary: 사용자에게 최적화 설정을 입력받아 반환하는 함수

    return:
        dict: 설정된 변수들을 포함한 딕셔너리
    """
    
    print(f'======= 현재는 기본 세팅값을 설정하는 화면입니다 =======')

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
        opt_range[f] = [mm.strip() for mm in min_max.split(",") if mm.strip()]
        
    necessary_feature = input('훈련에 사용될 조절 불가능한 변수를 설정해주세요. (쉼표로 구분, 기본값: 전체) : ')
    if necessary_feature.strip() == "":
        necessary_feature = []  # 또는 원하는 기본 리스트
    else:
        necessary_feature = [feat.strip() for feat in necessary_feature.split(",") if feat.strip()]
        

    # 숫자 입력 오류 방지를 위한 예외 처리 (입력하지 않으면 기본값 50 사용)
    try:
        limited_feature = int(input('모델 학습 시 최대로 사용할 Feature의 수를 설정해주세요 (기본값 : 50 ) : ') or 50)
    except ValueError:
        print("숫자가 입력되지 않아 기본값(50)으로 설정됩니다.")
        limited_feature = 50

    # 결과 반환
    return target_feature, controllable_feature, opt_range, necessary_feature, limited_feature
    