import yaml
import json
import os

def create_userinfo():


    # 사용자 이름과 이메일 입력 받기
    print(f'\n\n ======= 현재는 로그인 화면입니다 =======')
    user_name = input("사용자 이름을 입력하세요: ")
    user_email = input("사용자 이메일을 입력하세요: ")

    return user_name, user_email

    

