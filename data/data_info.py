import os
import json
import pandas as pd
import os.path as osp
from omegaconf import OmegaConf
from ydata_profiling import ProfileReport


def get_json(data, save_path='/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-22-lv3/ydata_profiling/base_user'):
    '''
    summary: ydata_profiling 라이브러리로 EDA 결과를 JSON 파일로 저장합니다.

    args:
        file_path (str): 입력 CSV 파일 경로.
        save_path (str): JSON 파일을 저장할 디렉터리 경로.

    return:
        str: 저장된 JSON 파일 경로.
    '''
    if not osp.exists(save_path):
        os.makedirs(save_path)
        print(f"폴더가 생성되었습니다: {save_path}")

    profile = ProfileReport(data, explorative=True)
    json_file_path = osp.join(save_path, 'EDA_analysis.json')
    profile.to_file(json_file_path)

    print(f"JSON 파일이 성공적으로 저장되었습니다: {json_file_path}")

    return json_file_path

    
def filter_json(json_file_path, base_config_path='/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-22-lv3/config/base_config.json'):
    '''
    summary: EDA 결과 JSON 파일을 불러와 필요한 변수 정보만 필터링한 후,
             별도의 기본 JSON에 필터링 결과를 추가하여 업데이트된 새로운 JSON 파일로 저장합니다.
    
    args:
        json_file_path (str): EDA 결과 JSON 파일 경로.
        base_config_path (str): 기본 설정 JSON 파일 경로 (없으면 새롭게 생성).
    
    return:
        tuple: (filtered_data, merged_file_path)
               filtered_data (dict): 필터링된 변수 정보 딕셔너리.
               merged_file_path (str): 업데이트된 merged JSON 파일 경로.
    '''
    # 1. 원본 EDA JSON 파일을 로드 (EDA 결과는 그대로 보존)
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

    # 4. 기본 설정에 필터링된 결과 추가 (예: 'filtered_result' 키 사용)
    base_config['filtered_result'] = filtered_data

    # 5. merged JSON 파일 경로 지정 (원본 EDA JSON은 그대로 두고, 새 파일로 저장)
    merged_file_path = os.path.join(os.path.dirname(json_file_path), 'merged_base_config.json')
    with open(merged_file_path, 'w', encoding='utf-8') as f:
        json.dump(base_config, f, indent=4)

    print(f"원본 EDA JSON 파일은 그대로 유지됩니다: {json_file_path}")
    print(f"필터링된 결과를 포함한 merged JSON 파일이 업데이트되었습니다: {merged_file_path}")

    return filtered_data, merged_file_path


if __name__ == "__main__":
    file_path = '/data/ephemeral/home/data/mat2.csv'
    save_path = '/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-22-lv3/eda/student_math'
    json_path = get_json(file_path, save_path)
    data_info = filter_json(json_path)