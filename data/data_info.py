import os
import json
import pandas as pd
import os.path as osp
from omegaconf import OmegaConf
from ydata_profiling import ProfileReport


def get_json(config, data, save_path='/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-22-lv3/ydata_profiling'):
    """
    summary: ydata_profiling 라이브러리로 EDA 결과를 JSON 파일로 저장합니다.

    args:
        config (dict): 설정 정보를 담은 딕셔너리 (여기서 user_name, user_email 키 사용)
        data (pd.DataFrame): 분석할 데이터
        save_path (str): JSON 파일을 저장할 디렉터리 경로

    return:
        str: 저장된 JSON 파일의 경로
    """

    # 디렉터리 유무 확인 후 생성
    if not osp.exists(save_path):
        os.makedirs(save_path)
        print(f"폴더가 생성되었습니다: {save_path}")

    # user_name, user_email 값이 config에 없을 경우 대비하여 기본값 설정
    user_name = config.get("user_name", "defaultUser")
    user_email = config.get("user_email", "defaultEmail")

    # 파일 이름 생성: user_name_user_email_EDA_analysis.json
    filename = f"{user_name}_{user_email}_EDA_analysis.json"
    json_file_path = osp.join(save_path, filename)

    # ydata_profiling을 사용해 EDA 진행 후 파일 생성
    profile = ProfileReport(data, explorative=True)
    profile.to_file(json_file_path)

    print(f"JSON 파일이 성공적으로 저장되었습니다: {json_file_path}")
    return json_file_path
    

def filter_json(config, json_file_path, base_config_path='/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-22-lv3/config/base_config.json'):
    """
    summary: EDA 결과 JSON 파일을 불러와 필요한 변수 정보만 필터링한 후,
             별도의 기본 JSON에 필터링 결과를 추가하여 업데이트된 새로운 JSON 파일로 저장합니다.
             최종적으로 기존 base_config.json 파일은 삭제합니다.
    
    args:
        config (dict): 사용자 설정 정보 (여기서 'user_name', 'user_email'를 사용)
        json_file_path (str): EDA 결과 JSON 파일 경로.
        base_config_path (str): 기본 설정 JSON 파일 경로 (없으면 새롭게 생성).
    
    return:
        tuple: (filtered_data, merged_file_path)
               filtered_data (dict): 필터링된 변수 정보 딕셔너리.
               merged_file_path (str): 업데이트된 merged JSON 파일 경로.
    """
    # 1. 원본 EDA JSON 파일 로드
    eda_data = OmegaConf.load(json_file_path)
    eda_data = OmegaConf.to_container(eda_data, resolve=True)

    # 2. EDA 결과에서 variables 항목 내 필요한 정보만 필터링
    filtered_data = {
        var_name: {
            'type': info.get('type', None),
            'p_missing': info.get('p_missing', None),
            'n_distinct': info.get('n_distinct', None),
            'p_distinct': info.get('p_distinct', None),
            'chi_squared': info.get('chi_squared', None),
            'mean': info.get('mean', None),
            'std': info.get('std', None),
            'variance': info.get('variance', None),
            'min': info.get('min', None),
            'max': info.get('max', None),
            'kurtosis': info.get('kurtosis', None),
            'skewness': info.get('skewness', None),
            'mad': info.get('mad', None),
            'range': info.get('range', None),
            'iqr': info.get('iqr', None)
        }
        for var_name, info in eda_data.get('variables', {}).items() if var_name != 'Unnamed: 0'
    }

    # 3. 기본 설정 파일(base_config.json)이 존재하면 불러오고, 없으면 빈 딕셔너리 생성
    if os.path.exists(base_config_path):
        with open(base_config_path, 'r', encoding='utf-8') as f:
            base_config = json.load(f)
    else:
        base_config = {}

    # 4. 기본 설정에 필터링된 결과 추가
    base_config['filtered_result'] = filtered_data

    # 4-1. 사용자 이름, 이메일 불러오기 (없으면 기본값)
    user_name = config.get("user_name", "defaultName")
    user_email = config.get("user_email", "defaultEmail")

    # 5. merged JSON 파일 경로 지정
    #   "user_name_user_email_merged_base_config.json" 형태로 파일명 구성
    merged_filename = f"{user_name}_{user_email}_merged_base_config.json"
    merged_file_path = os.path.join(os.path.dirname(json_file_path), merged_filename)

    with open(merged_file_path, 'w', encoding='utf-8') as f:
        json.dump(base_config, f, indent=4)

    print(f"원본 EDA JSON 파일은 그대로 유지됩니다: {json_file_path}")
    print(f"필터링된 결과를 포함한 merged JSON 파일이 업데이트되었습니다: {merged_file_path}")

    # 6. 기존 base_config.json 파일 삭제
    if os.path.exists(base_config_path):
        try:
            os.remove(base_config_path)
            print(f"기존 설정 파일을 삭제했습니다: {base_config_path}")
        except Exception as e:
            print(f"기존 설정 파일 삭제 중 에러가 발생했습니다: {e}")

    return filtered_data, merged_file_path


if __name__ == "__main__":
    file_path = '/data/ephemeral/home/data/mat2.csv'
    save_path = '/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-22-lv3/eda/student_math'
    json_path = get_json(file_path, save_path)
    data_info = filter_json(json_path)