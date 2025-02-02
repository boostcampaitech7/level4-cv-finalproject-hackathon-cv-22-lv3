import os
import json
import pandas as pd
import os.path as osp
from omegaconf import OmegaConf
from ydata_profiling import ProfileReport

def get_json(data, save_path='/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-22-lv3/EDA/base_user'):
    """
    summary: ydata_profiling 라이브러리로 EDA 결과를 JSON 파일로 저장합니다.

    args:
        data (pd.DataFrame): 입력 데이터 (CSV 파일 경로가 아닌 DataFrame이어야 함)
        save_path (str): JSON 파일을 저장할 디렉터리 경로.

    return:
        str: 저장된 JSON 파일 경로.
    """
    if not osp.exists(save_path):
        os.makedirs(save_path)
        print(f"폴더가 생성되었습니다: {save_path}")

    profile = ProfileReport(data, explorative=True)
    json_file_path = osp.join(save_path, 'result.json')
    profile.to_file(json_file_path)

    print(f"JSON 파일이 성공적으로 저장되었습니다: {json_file_path}")

    return json_file_path


def filter_json(json_file_path):
    """
    summary: JSON 파일을 불러와 필요한 변수 정보만 필터링한 후,
             기존 base_config.json 파일에 추가합니다.

    args:
        json_file_path (str): EDA 결과 JSON 파일 경로.

    return:
        dict: 필터링된 변수 정보 딕셔너리.
    """
    # EDA 결과 JSON 파일을 OmegaConf로 로드 후 일반 dict로 변환
    data = OmegaConf.load(json_file_path)
    data = OmegaConf.to_container(data, resolve=True)
    
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
        for var_name, info in data.get('variables', {}).items() if var_name != 'Unnamed: 0'
    }
    
    # base_config.json 파일 경로 (기본 설정 파일)
    base_config_path = json_file_path
    # base_config.json이 존재하면 로드, 없으면 빈 딕셔너리 생성
    if os.path.exists(base_config_path):
        with open(base_config_path, 'r', encoding='utf-8') as f:
            base_config = json.load(f)
    else:
        base_config = {}

    # 필터링된 EDA 정보를 기존 설정에 추가 (예: 'eda_filtered' 키 사용)
    base_config['eda_filtered'] = filtered_data

    # 업데이트된 설정을 다시 base_config.json에 저장
    with open(base_config_path, 'w', encoding='utf-8') as f:
        json.dump(base_config, f, indent=4)

    print(f"Base configuration updated with filtered EDA data: {base_config_path}")

    return filtered_data


if __name__ == "__main__":
    # CSV 파일을 읽어서 DataFrame으로 변환 (get_json 함수는 DataFrame을 인자로 사용합니다)
    csv_path = '/data/ephemeral/home/data/mat2.csv'
    try:
        df = pd.read_csv(csv_path)
        print(f"Data loaded from {csv_path}")
    except Exception as e:
        print(f"Failed to load data from {csv_path}: {e}")
        exit(1)
    
    save_path = '/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-22-lv3/EDA/base_user'
    # EDA 결과를 JSON 파일로 저장
    json_path = get_json(df, save_path)
    
    # 저장된 EDA 결과를 필터링하고 base_config.json에 추가
    data_info = filter_json(json_path)