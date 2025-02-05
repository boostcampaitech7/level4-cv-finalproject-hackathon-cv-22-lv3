import yaml
import json
import os

def model_base_setting():

    print(f'\n\n ======= 현재는 모델 세팅 화면 입니다. =======')
    model_quality = int(input("""모델의 퀄리티를 설정해주세요  \n "0": "best_quality"\n "1": "high_quality"\n"2": "good_quality"\n"3": "medium_quality": 4 \n [answer] : """))
    time_to_train = int(input("학습할 시간을 설정해주세요 (초): "))

    return time_to_train, model_quality

    

