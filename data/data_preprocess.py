import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, StandardScaler


class DataPreprocessor:
    '''
    summary: 데이터 전처리를 위한 클래스. 이상치 처리, 결측치 처리, 
             변수 특성별 처리를 수행합니다.

    args: 
        scaling_method (str): 스케일링 방법 선택 ('standard', 'minmax').
    '''
    def __init__(self, scaling_method="standard"):
        '''
        summary: DataPreprocessor 클래스 초기화 함수.

        args:
            scaling_method (str): 'standard' 또는 'minmax' 중 하나를 선택해 스케일링 방식을 설정합니다.
        '''
        self.scaling_method = scaling_method
        self.label_encoders = {}
        self.scalers = {}

    def remove_outliers(self, df, columns, z_thresh=3):
        '''
        summary: 지정된 열에서 z-score를 기준으로 이상치를 제거합니다.

        args: 
            df (pd.DataFrame): 입력 데이터프레임.
            columns (list): 이상치를 제거할 열 이름 목록.
            z_thresh (float): z-score 임계값. 기본값은 3입니다.
        
        return: 
            pd.DataFrame: 이상치가 제거된 데이터프레임.
        '''
        for col in columns:
            z_scores = (df[col] - df[col].mean()) / df[col].std()
            df = df[np.abs(z_scores) <= z_thresh]
        return df

    def handle_missing_values(self, df):
        '''
        summary: 결측치를 열별로 처리합니다. 결측치 비율에 따라 행 삭제 또는 대체 기법을 적용합니다.

        args: 
            df (pd.DataFrame): 입력 데이터프레임.
        
        return: 
            pd.DataFrame: 결측치가 처리된 데이터프레임.
        '''
        for col in df.columns:
            missing_ratio = df[col].isnull().sum() / len(df)
            
            if missing_ratio < 0.03:
                # 결측치 비율이 3% 미만이면 행 삭제
                df = df.dropna(subset=[col])
            else:
                # 결측치 비율이 3% 이상이면 대체 방법 사용
                if df[col].dtype in ['int64', 'float64']:
                    # 수치형 데이터는 KNN Imputer로 처리
                    imputer = KNNImputer(n_neighbors=3)
                    df[[col]] = imputer.fit_transform(df[[col]])
                else:
                    # 범주형 데이터는 최빈값으로 대체
                    mode_value = df[col].mode()[0]
                    df[col] = df[col].fillna(mode_value)

        return df

    def process_features(self, df):
        '''
        summary: 범주형 변수는 라벨 인코딩, 수치형 변수는 스케일링을 수행합니다.

        args: 
            df (pd.DataFrame): 입력 데이터프레임.
        
        return: 
            pd.DataFrame: 처리된 데이터프레임.
        '''
        

        return df


if __name__ == "__main__":
    # CSV 파일 로드
    df = pd.read_csv("/data/ephemeral/home/.cache/kagglehub/datasets/henryshan/student-performance-prediction/versions/2/mat2.csv")

    # 데이터 전처리 객체 생성
    preprocessor = DataPreprocessor(scaling_method="standard")

    # 이상치 처리
    df = preprocessor.remove_outliers(df, columns=["column1", "column2"])

    # 결측치 처리
    df = preprocessor.handle_missing_values(df, strategy="mean")

    # 특성별 처리 (범주형과 수치형 열 지정)
    # df = preprocessor.process_features(df)

    # 처리 결과 출력
    print(df.head())
