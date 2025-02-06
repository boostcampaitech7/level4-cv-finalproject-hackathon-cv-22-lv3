import os
import json
import pandas as pd
import os.path as osp
from omegaconf import OmegaConf
from ydata_profiling import ProfileReport
import logging


# def get_json(config, data, save_path='/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-22-lv3/ydata_profiling'):
#     """
#     summary: ydata_profiling 라이브러리로 EDA 결과를 JSON 및 HTML 파일로 저장합니다.

#     args:
#         config (dict): 설정 정보를 담은 딕셔너리 (여기서 user_name, user_email 키 사용)
#         data (pd.DataFrame): 분석할 데이터
#         save_path (str): JSON 및 HTML 파일을 저장할 디렉터리 경로

#     return:
#         tuple: (json_file_path, eda_html_path) 저장된 JSON 및 HTML 파일 경로
#     """

#     # 디렉터리 유무 확인 후 생성
#     if not osp.exists(save_path):
#         os.makedirs(save_path)
#         print(f"폴더가 생성되었습니다: {save_path}")

#     # user_name, user_email 값이 config에 없을 경우 대비하여 기본값 설정
#     user_name = config.get("user_name", "defaultUser")
#     user_email = config.get("user_email", "defaultEmail")

#     # 파일 이름 생성
#     json_filename = f"{user_name}_{user_email}_EDA_analysis.json"
#     eda_html_filename = f"{user_name}_{user_email}_EDA_analysis.html"

#     json_file_path = osp.join(save_path, json_filename)
#     eda_html_path = osp.join(save_path, eda_html_filename)

#     # ydata_profiling을 사용해 EDA 진행 후 JSON 및 HTML 파일 생성
#     profile = ProfileReport(data, explorative=True)
    
#     # JSON 파일 저장
#     profile.to_file(json_file_path)

#     # HTML 파일 저장
#     profile.to_file(eda_html_path)

#     print(f"JSON 파일이 성공적으로 저장되었습니다: {json_file_path}")
#     print(f"HTML 파일이 성공적으로 저장되었습니다: {eda_html_path}")

#     return json_file_path, eda_html_path
    

# def filter_json(config, base_config_path='/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-22-lv3/config/base_config.json'):
#     """
#     summary: EDA 결과 JSON 파일을 불러와 필요한 변수 정보만 필터링한 후,
#              별도의 기본 JSON에 필터링 결과를 추가하여 업데이트된 새로운 JSON 파일로 저장합니다.
#              최종적으로 기존 base_config.json 파일은 삭제합니다.
    
#     args:
#         config (dict): 사용자 설정 정보 (여기서 'user_name', 'user_email'를 사용)
#         json_file_path (str): EDA 결과 JSON 파일 경로.
#         base_config_path (str): 기본 설정 JSON 파일 경로 (없으면 새롭게 생성).
    
#     return:
#         tuple: (filtered_data, merged_file_path)
#                filtered_data (dict): 필터링된 변수 정보 딕셔너리.
#                merged_file_path (str): 업데이트된 merged JSON 파일 경로.
#     """
#     # 1. 원본 EDA JSON 파일 로드
#     eda_data = OmegaConf.load(config)
#     eda_data = OmegaConf.to_container(eda_data, resolve=True)

#     # 2. EDA 결과에서 variables 항목 내 필요한 정보만 필터링
#     filtered_data = {
#         var_name: {
#             'type': info.get('type', None),
#             'p_missing': info.get('p_missing', None),
#             'n_distinct': info.get('n_distinct', None),
#             'p_distinct': info.get('p_distinct', None),
#             'chi_squared': info.get('chi_squared', None),
#             'mean': info.get('mean', None),
#             'std': info.get('std', None),
#             'variance': info.get('variance', None),
#             'min': info.get('min', None),
#             'max': info.get('max', None),
#             'kurtosis': info.get('kurtosis', None),
#             'skewness': info.get('skewness', None),
#             'mad': info.get('mad', None),
#             'range': info.get('range', None),
#             'iqr': info.get('iqr', None)
#         }
#         for var_name, info in eda_data.get('variables', {}).items() if var_name != 'Unnamed: 0'
#     }

#     # 3. 기본 설정 파일(base_config.json)이 존재하면 불러오고, 없으면 빈 딕셔너리 생성
#     if os.path.exists(base_config_path):
#         with open(base_config_path, 'r', encoding='utf-8') as f:
#             base_config = json.load(f)
#     else:
#         base_config = {}

#     # 4. 기본 설정에 필터링된 결과 추가
#     base_config['filtered_result'] = filtered_data

#     # 4-1. 사용자 이름, 이메일 불러오기 (없으면 기본값)
#     user_name = config.get("user_name", "defaultName")
#     user_email = config.get("user_email", "defaultEmail")

#     # 5. merged JSON 파일 경로 지정
#     #   "user_name_user_email_merged_base_config.json" 형태로 파일명 구성
#     merged_filename = f"{user_name}_{user_email}_merged_base_config.json"
#     merged_file_path = os.path.join(os.path.dirname(config), merged_filename)

#     with open(merged_file_path, 'w', encoding='utf-8') as f:
#         json.dump(base_config, f, indent=4)

#     print(f"원본 EDA JSON 파일은 그대로 유지됩니다: {config}")
#     print(f"필터링된 결과를 포함한 merged JSON 파일이 업데이트되었습니다: {merged_file_path}")

#     # 6. 기존 base_config.json 파일 삭제
#     if os.path.exists(base_config_path):
#         try:
#             os.remove(base_config_path)
#             print(f"기존 설정 파일을 삭제했습니다: {base_config_path}")
#         except Exception as e:
#             print(f"기존 설정 파일 삭제 중 에러가 발생했습니다: {e}")

#     return filtered_data, merged_file_path


# if __name__ == "__main__":
#     file_path = '/data/ephemeral/home/data/mat2.csv'
#     save_path = '/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-22-lv3/eda/student_math'
#     json_path = get_json(file_path, save_path)
#     data_info = filter_json(json_path)



def get_json(user_name, user_email, data_path, save_path='/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-22-lv3/ydata_profiling'):
    """
    summary: ydata_profiling 라이브러리로 EDA 결과를 JSON 및 HTML 파일로 저장합니다.

    args:
        config (dict): 설정 정보를 담은 딕셔너리 (여기서 user_name, user_email 키 사용)
        data (pd.DataFrame): 분석할 데이터
        save_path (str): JSON 및 HTML 파일을 저장할 디렉터리 경로

    return:
        tuple: (json_file_path, eda_html_path) 저장된 JSON 및 HTML 파일 경로
    """
    try:
        data = pd.read_csv(data_path)
        logging.info(f"Data loaded from {data_path}")
    except Exception as e:
        logging.error(f"Failed to load data: {e}")
        return

    # 디렉터리 유무 확인 후 생성
    if not osp.exists(save_path):
        os.makedirs(save_path)
        print(f"폴더가 생성되었습니다: {save_path}")

    # user_name, user_email 값이 config에 없을 경우 대비하여 기본값 설정
    user_name = user_name
    user_email = user_email

    # 파일 이름 생성
    json_filename = f"{user_name}_{user_email}_config.json"
    eda_html_filename = f"{user_name}_{user_email}_EDA_analysis.html"

    json_file_path = osp.join(save_path, json_filename)
    eda_html_path = osp.join(save_path, eda_html_filename)

    # ydata_profiling을 사용해 EDA 진행 후 JSON 및 HTML 파일 생성
    profile = ProfileReport(data, explorative=True)
    
    # JSON 파일 저장
    profile.to_file(json_file_path)

    # HTML 파일 저장
    profile.to_file(eda_html_path)

    print(f"JSON 파일이 성공적으로 저장되었습니다: {json_file_path}")
    print(f"HTML 파일이 성공적으로 저장되었습니다: {eda_html_path}")

    return json_file_path, eda_html_path


def filter_json(config):
    """
    하나의 config에 모든 정보가 담겨 있으므로, 해당 config에서
    "variables" 항목 내 필요한 정보만 필터링한 후, 이를 config에 추가하고,
    새로운 merged JSON 파일(merged_file_path)을 생성하여 저장합니다.
    
    Args:
        config (dict): 모든 설정 정보와 EDA 결과를 담고 있는 config 딕셔너리.
                       예를 들어, config에는 'variables', 'user_name', 'user_email' 등이 포함되어 있어야 합니다.
        merged_dir (str, optional): merged 파일을 저장할 디렉토리.
                                    지정하지 않으면 현재 작업 디렉토리를 사용합니다.
    
    Returns:
        tuple: (filtered_data, merged_file_path)
            filtered_data (dict): 필터링된 변수 정보 딕셔너리.
            merged_file_path (str): 업데이트된 merged JSON 파일의 경로.
    """
    # 1. config 내의 "variables" 항목에서 필요한 정보만 필터링
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
            'iqr': info.get('iqr', None),
            'range': info.get('range', None),
            'Q1': info.get('25%', None),
            'Q3': info.get('75%', None)
        }
        for var_name, info in config.get('variables', {}).items()
    }
    
    # 2. config에 필터링된 결과 추가
    config['filtered_result'] = filtered_data
    
    # 3. 사용자 이름, 이메일 추출 (기본값 지정)
    user_name = config.get("user_name", "defaultName")
    user_email = config.get("user_email", "defaultEmail")
    
    # 4. merged JSON 파일명을 생성
    merged_filename = f"{user_name}_{user_email}_merged_config.json"
    
    merged_file_path = os.path.join('/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-22-lv3/ydata_profiling', merged_filename)
    
    # 6. config를 새로운 merged JSON 파일로 저장
    with open(merged_file_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    
    print(f"config 파일에 필터링된 결과가 업데이트되었습니다: {merged_file_path}")
    
    return filtered_data, merged_file_path



if __name__ == "__main__":
    config = OmegaConf.load('/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-22-lv3/config/user_config.json')
    file_path = '/data/ephemeral/home/data/WA_Fn-UseC_-HR-Employee-Attrition.csv'
    save_path = '/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-22-lv3/ydata_profiling'
    json_path = get_json(config, file_path, save_path)
    data_info = filter_json(json_path)
