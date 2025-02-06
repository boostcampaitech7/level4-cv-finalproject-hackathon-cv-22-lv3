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


    def remove_outliers(self, col):
        '''
        summary: 지정된 열에서 IQR(Interquartile Range)를 기준으로 이상치를 제거합니다.

        args: 
            col (list): 이상치를 제거할 열 이름 목록.

        return: 
            pd.DataFrame: 이상치가 제거된 데이터프레임.
        '''
        feature = self.data_info[col]

        if feature["type"] == "Numeric":
            Q1 = feature["Q1"]
            Q3 = feature["Q3"]
            IQR = feature["iqr"]
            kurtosis = feature["kurtosis"]
            
            if kurtosis > 5:
                lower_bound = Q1 - 3.0 * IQR
                upper_bound = Q3 + 3.0 * IQR
                
                self.data = self.data[(self.data[col] >= lower_bound) & (self.data[col] <= upper_bound)]
            
            elif kurtosis < 1:
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
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
        if not np.issubdtype(self.data[col].dtype, np.integer):    
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

        if skewness >= 1:
            power_transformer = PowerTransformer(method='yeo-johnson')
            transformed = power_transformer.fit_transform(self.data[[col]])

            standard_scaler = StandardScaler()
            self.data[[col]] = standard_scaler.fit_transform(transformed)

            self.decoders[col] = {
                "encoder" : [power_transformer, standard_scaler]
            }
        else:
            standard_scaler = StandardScaler()
            self.data[[col]] = standard_scaler.fit_transform(self.data[[col]])
        
            self.decoders[col] = {
                "encoder" : standard_scaler
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
            'encoder': [f'{col}_year', f'{col}_month', f'{col}_day']
            }

    def process_features(self, strategy="mean"):
        '''
        summary: 모든 열에 대해 전처리를 수행하고, 인코더 정보가 담긴 디코더를 반환합니다.

        return: 
            pd.DataFrame: 전처리가 완료된 데이터프레임.
            Dict : 인코더 정보가 담긴 디코더.
        '''
        original_columns = list(self.data.columns)
        
        for col in original_columns:
            self.handle_missing_values(col, strategy)
            self.remove_outliers(col)
            processed_df = self.process_column(col)
            
        return processed_df

    def decode(self, df):
        '''
        summary: 데이터 전처리 과정에서 변환된 값을 원래 값으로 복원합니다.

        args:
            pd.DataFrame (str) : 복원을 진행할 데이터프레임

        return:
            pd.DataFrame: 디코딩이 완료된 데이터프레임.
        '''
        columns = list(df.columns)
        for col in columns:
            
            if col not in self.decoders:
                continue

            feature = self.data_info[col]
            feature_type = feature['type']

            encoder_info = self.decoders[col]
            encoder = encoder_info['encoder']

            if (feature_type == 'Categorical') or (feature_type == 'Boolean'):
                df[col] = encoder.inverse_transform(df[col])
            
            elif feature_type == 'Numeric':
                if isinstance(encoder, list) and len(encoder) == 2:
                    power_transformer, standard_scaler = encoder
                    df[[col]] = standard_scaler.inverse_transform(df[[col]])
                    df[[col]] = power_transformer.inverse_transform(df[[col]])

                else:
                    standard_scaler = encoder
                    df[[col]] = standard_scaler.inverse_transform(df[[col]])

            elif feature_type == 'DateTime':
                year_col, month_col, day_col = encoder_info['encoder']
                
                df[col] = pd.to_datetime(
                    df[[year_col, month_col, day_col]].astype(str).agg('-'.join, axis=1),
                    errors='coerce'
                )

                # 변환된 연, 월, 일 컬럼 삭제
                df.drop(columns=encoder_info['encoder'], inplace=True)

        return df
    

if __name__ == "__main__":
    # CSV 파일 로드
    df = pd.read_csv("/data/ephemeral/home/data/WA_Fn-UseC_-HR-Employee-Attrition.csv")

    # 데이터 EDA 정보를 JSON에서 로드
    data_info = OmegaConf.load('/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-22-lv3/ydata_profiling/user_user@xx.com_merged_base_config.json')

    preprocessor = DataPreprocessor(df, data_info)

    # 결측치, 이상치, 특성별 전처리 수행
    processed_df = preprocessor.process_features(strategy="knn")

    # 처리 결과 출력
    print("===================== 인코딩 후 데이터 정보 =====================")
    print(processed_df.head())

    decoded_df = preprocessor.decode(processed_df)

    print("===================== 디코딩 후 데이터 정보 =====================")
    print(decoded_df.head())
    print(decoded_df.info())