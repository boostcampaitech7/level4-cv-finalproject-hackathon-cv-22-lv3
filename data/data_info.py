import os
import json
import pandas as pd
import os.path as osp
from omegaconf import OmegaConf
from ydata_profiling import ProfileReport


def get_json(file_path, save_path):
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

    df = pd.read_csv(file_path)
    profile = ProfileReport(df, explorative=True)
    json_file_path = osp.join(save_path, 'result.json')
    profile.to_file(json_file_path)

    print(f"JSON 파일이 성공적으로 저장되었습니다: {json_file_path}")

    return json_file_path


def filter_json(json_file_path):
    '''
    summary: JSON 파일을 불러와 필요한 변수 정보만 필터링한 후 저장합니다.

    args:
        json_file_path (str): EDA 결과 JSON 파일 경로.

    return:
        dict: 필터링된 변수 정보 딕셔너리.
    '''
    data = OmegaConf.load(json_file_path)
    data = OmegaConf.to_container(data, resolve=True)  # DictConfig -> 일반 딕셔너리
    filtered_data = {
        var_name : {
            # 데이터 타입
            'type' : info.get('type', None),
            # 결측치 비율
            'p_missing' : info.get('p_missing', None),
            # 고유값 개수 (범주형 -> 인코딩 방식 선택)
            'n_distinct' : info.get('n_distinct', None),
            # 고유값 비율 (수치형 중 이산, 연속 구분)
            'p_distinct' : info.get('p_distinct', None),
            # 카이 제곱 검정
            'chi_squared' : info.get('chi_squared', None),
            # 평균
            'mean' : info.get('mean', None),
            # 표준편차
            'std' : info.get('std', None),
            # 분산
            'variance' : info.get('variance', None),
            # 최소값
            'min' : info.get('min', None),
            # 최대값
            'max' : info.get('max', None),
            # 첨도
            'kurtosis' : info.get('kurtosis', None),
            # 왜도
            'skewness' : info.get('skewness', None),
            # 중앙값
            'mad' : info.get('mad', None),
            # 범위
            'range' : info.get('range', None),
            # 4분위
            'iqr' : info.get('iqr', None)
        }
        for var_name, info in data.get('variables', {}).items() if var_name != 'Unnamed: 0'
        }
    
    filtered_json_path = os.path.join(os.path.dirname(json_file_path), 'filtered_result.json')
    # 필터링된 결과를 JSON 파일로 저장
    with open(filtered_json_path, 'w') as json_file:
        json.dump(filtered_data, json_file, indent=4)

    print(f"필터링된 데이터가 JSON 파일로 저장되었습니다: {filtered_json_path}")

    return filtered_data


if __name__ == "__main__":
    file_path = '/data/ephemeral/home/data/mat2.csv'
    save_path = '/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-22-lv3/eda/student_math'
    json_path = get_json(file_path, save_path)
    data_info = filter_json(json_path)