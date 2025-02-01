import numpy as np
import pandas as pd
from datetime import datetime
from omegaconf import OmegaConf
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, MinMaxScaler, StandardScaler, PowerTransformer


class DataPreprocessor:
    '''
    summary: 데이터 전처리를 위한 클래스. 이상치 처리, 결측치 처리, 
             변수 특성별 처리를 수행합니다.
    '''
    def __init__(self, df, data_info):
        '''
        args:
            df (pd.DataFrame): 원본 데이터.
            data_info (dict): 각 열의 전처리 정보를 담은 딕셔너리.
        '''
        self.data = df
        self.data_info = data_info
        self.decoders = {}

    def remove_outliers(self, columns):
        '''
        summary: 지정된 열에서 IQR(Interquartile Range)를 기준으로 이상치를 제거합니다.

        args: 
            columns (list): 이상치를 제거할 열 이름 목록.

        return: 
            pd.DataFrame: 이상치가 제거된 데이터프레임.
        '''
        for col in columns:
            feature = self.data_info[col]

            # 수치형 변수만 처리
            if feature["type"] == "Numeric":
                # Q1, Q3 및 IQR 계산
                Q1 = self.data[col].quantile(0.25)
                Q3 = self.data[col].quantile(0.75)
                IQR = Q3 - Q1

                # 이상치 기준 계산
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR

                # 이상치 제거
                self.data = self.data[(self.data[col] >= lower_bound) & (self.data[col] <= upper_bound)]

        return self.data

    def handle_missing_values(self, col, strategy="mean"):
        '''
        summary: 결측치를 열별로 처리합니다. 결측치 비율에 따라 행 삭제 또는 대체 기법을 적용합니다.

        args: 
            df (pd.DataFrame): 입력 데이터프레임.
            strategy (str): 결측치 처리 방법 ('mean', 'median', 'mode', 'knn').
        
        return: 
            pd.DataFrame: 결측치가 처리된 데이터프레임.
        '''
        feature = self.data_info[col]
        missing_ratio = feature["p_missing"]            
        
        if missing_ratio < 0.03:
            self.data = self.data.dropna(subset=[col])  # 결측치 비율이 3% 미만이면 행 삭제
        else:
            if strategy in ['mean', 'median', 'mode']:
                if feature["type"] == "Numeric":
                    imputer = SimpleImputer(strategy=strategy)
                else:
                    # 범주형 데이터는 항상 최빈값으로 처리
                    imputer = SimpleImputer(strategy="most_frequent")
            elif strategy == "knn":
                imputer = KNNImputer(n_neighbors=3)
            else:
                raise ValueError("Invalid strategy. Choose from 'mean', 'median', 'mode', 'knn'.")
            
            self.data[[col]] = imputer.fit_transform(self.data[[col]])
        
        return self.data

    def process_column(self, col):
        '''
        summary: 각 열의 특성(type)을 기반으로 적절한 전처리를 수행합니다.

        args:
            col (str): 처리할 열 이름.

        return:
            pd.DataFrame: 전처리가 완료된 데이터프레임.
        '''
        feature = self.data_info[col]
        feature_type = feature['type']

        n_distinct = feature['n_distinct']

        if n_distinct == 1:
            self.data.drop(columns=[col], inplace=True)
            return

        if feature_type == 'Categorical' or feature_type == 'Boolean':
            self._categorical_features(col)
        
        elif feature_type == 'Numeric':
            self._numeric_features(col)
        
        elif feature_type == 'DateTime':
            self._date_features(col)
                
        return self.data

    def _categorical_features(self, col):
        '''
        summary: 범주형 변수를 처리하는 함수. 
                 고유값 개수(n_distinct)에 따라 OneHotEncoder 또는 LabelEncoder를 적용합니다.

        args:
            col (str): 처리할 열 이름.

        return:
            None: 데이터프레임을 직접 수정하며, 인코더 정보를 self.decoders에 저장합니다.
        '''
        # Label Encoding 적용
        le = LabelEncoder()
        self.data[col] = le.fit_transform(self.data[col])
        
        # 인코더 정보 저장
        self.decoders[col] = {
            'encoder': le,
            }

    def _numeric_features(self, col):
        '''
        summary: 수치형 변수를 처리하는 함수. 
                데이터의 왜도(skewness)에 따라 적절한 변환을 적용합니다.

        args:
            col (str): 처리할 열 이름.

        return:
            None: 데이터프레임을 직접 수정하며, 인코더 정보를 self.decoders에 저장합니다.
        '''
        skewness = abs(self.data_info[col]['skewness'])
        transformer = None

        if skewness >= 1:
            transformer = PowerTransformer(method='yeo-johnson')
        elif skewness < 0.5:
            transformer = StandardScaler()
        
        if transformer:
            self.data[[col]] = transformer.fit_transform(self.data[[col]])
        
        # 항상 MinMaxScaler 적용 (0~1 범위로 정규화)
        min_max_scaler = MinMaxScaler()
        self.data[[col]] = min_max_scaler.fit_transform(self.data[[col]])

        self.decoders[col] = {
            "encoder" : [min_max_scaler, transformer]
            }

    def _date_features(self, col):
        '''
        summary: DateTime 열을 년, 월, 일로 나누어 개별 숫자형 변수로 변환합니다. 
             이를 통해 모델이 날짜 정보를 학습할 수 있도록 돕습니다.

        args:
            col (str): 처리할 열 이름.

        return:
            None: 데이터프레임을 직접 수정하며, 인코더 정보를 self.decoders에 저장합니다.
        '''        
        # 현재 연도 가져오기 (기본값 설정용)
        current_year = datetime.now().year
        
        self.data[col] = pd.to_datetime(self.data[col], errors='coerce')

        self.data[f'{col}_year'] = self.data[col].dt.year.fillna(current_year).astype(int)
        self.data[f'{col}_month'] = self.data[col].dt.month.fillna(1).astype(int)  # 월이 없으면 1월
        self.data[f'{col}_day'] = self.data[col].dt.day.fillna(1).astype(int)  # 일이 없으면 1일
        
        self.data.drop(columns=[col], inplace=True)
        
        self.decoders[col] = {
            'columns': [f'{col}_year', f'{col}_month', f'{col}_day']
            }

    def process_features(self, strategy="mean"):
        '''
        summary: 모든 열에 대해 전처리를 수행합니다.

        return: 
            pd.DataFrame: 전처리가 완료된 데이터프레임.
        '''
        original_columns = list(self.data.columns)
        
        for col in original_columns:
            self.handle_missing_values(col, strategy)
            processed_df = self.process_column(col)
            
        return processed_df    

    def decode(self, col):
        '''
        summary: 데이터 전처리 과정에서 변환된 값을 원래 값으로 복원합니다.

        args:
            col (str): 원래 값으로 복원할 열 이름.

        return:
            pd.DataFrame: 디코딩이 완료된 데이터프레임.
        '''
        if col not in self.decoders:
            return self.data

        feature = self.data_info[col]
        feature_type = feature['type']

        encoder_info = self.decoders[col]
        encoder = encoder_info['encoder'] if 'encoder' in encoder_info else encoder_info['columns']

        if (feature_type == 'Categorical') or (feature_type == 'Boolean'):
            self.data[col] = encoder.inverse_transform(self.data[col])
        
        elif feature_type == 'Numeric':
            min_max_scaler, transfomer = encoder
            self.data[[col]] = min_max_scaler.inverse_transform(self.data[[col]])
            
            if transfomer:
                self.data[[col]] = transfomer.inverse_transform(self.data[[col]])
        
        elif feature_type == 'DateTime':
            year_col, month_col, day_col = encoder_info['columns']
            
            self.data[col] = pd.to_datetime(
                self.data[[year_col, month_col, day_col]].astype(str).agg('-'.join, axis=1),
                errors='coerce'
            )
    
            # 변환된 연, 월, 일 컬럼 삭제 (선택 사항)
            self.data.drop(columns=encoder_info['columns'], inplace=True)

        return self.data
    

if __name__ == "__main__":
    # CSV 파일 로드
    df = pd.read_csv("/data/ephemeral/home/data/time/DailyDelhiClimateTrain.csv")
    print("초기 데이터 정보:")
    print(df.head())
    print(df.info())

    # 데이터 EDA 정보를 JSON에서 로드
    data_info = OmegaConf.load('/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-22-lv3/eda/time_data/filtered_result.json')

    # 데이터 전처리 객체 생성
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])
        print('"Unnamed: 0" 열이 삭제되었습니다.')
    else:
        print('"Unnamed: 0" 열이 존재하지 않습니다.')        

    preprocessor = DataPreprocessor(df, data_info)

    # 이상치 처리 
    print(f"데이터의 feature들: {df.columns.tolist()}")
    cols = df.columns.tolist()
    print(f"처리 전 데이터 크기: {df.shape}")
    # df = preprocessor.remove_outliers(df, columns=cols)  # remove_outliers 필요시 활성화

    # 특성별 전처리 수행
    processed_df = preprocessor.process_features(strategy="knn")

    # 처리 결과 출력
    print("처리 후 데이터 정보:")
    print(processed_df.info())
    print(processed_df.head())

    # 디코딩 후 결과 출력
    for col in cols: 
        decoded_df = preprocessor.decode(col)
    
    print("디코딩 후 데이터 정보:")
    print(decoded_df.info())
    print(decoded_df.head())