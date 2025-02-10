import numpy as np
import pandas as pd
from datetime import datetime
from omegaconf import OmegaConf
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.preprocessing import RobustScaler, LabelEncoder, StandardScaler, PowerTransformer


class DataPreprocessor:
    '''
    summary: 데이터 전처리를 위한 클래스. 이상치 처리, 결측치 처리, 
             변수 특성별 처리를 수행합니다.
    '''
    def __init__(self, df, config):
        '''
        args:
            df (pd.DataFrame): 원본 데이터.
            data_info (dict): 각 열의 전처리 정보를 담은 딕셔너리.
        '''
        self.data = df
        self.data_info = config["filtered_data"]
        self.decoders = {}

    def remove_outliers(self, col):
        '''
        summary: 지정된 열에서 IQR(Interquartile Range)를 기준으로 이상치를 제거합니다.

        args: 
            cols (list): 이상치를 제거할 열 이름 목록.

        return: 
            pd.DataFrame: 이상치가 제거된 데이터프레임.
        '''
        feature = self.data_info[col]

        if feature["type"] == "Numeric":
            kurtosis = feature["kurtosis"]
            
            if kurtosis > 3:
                robust_scaler = RobustScaler()
                
                self.data[[col]] = robust_scaler.fit_transform(self.data[[col]])

                self.decoders[col] = {
                    "outliers" : robust_scaler
                }

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

        if feature_type == 'Categorical' or feature_type == 'Boolean':
            self._categorical_features(col)
        
        elif feature_type == 'Numeric':
            self._numeric_features(col)
        
        elif feature_type == 'DateTime':
            self._date_features(col)
        
        elif feature_type == 'Text':
            self._text_features(col)

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
        skewness = abs(self.data_info[col]['skewness'])
        
        if skewness >= 1:
            power_transformer = PowerTransformer(method='yeo-johnson')
            transformed = power_transformer.fit_transform(self.data[[col]])
            standard_scaler = StandardScaler()
            self.data[[col]] = standard_scaler.fit_transform(transformed)
            
            # 이미 outlier scaler가 존재하는 경우 결합하여 저장
            if col in self.decoders and "outliers" in self.decoders[col]:
                outlier_scaler = self.decoders[col]["outliers"]
                self.decoders[col] = {
                    "encoder": [outlier_scaler, power_transformer, standard_scaler]
                }
            else:
                self.decoders[col] = {
                    "encoder": [power_transformer, standard_scaler]
                }
        else:
            standard_scaler = StandardScaler()
            self.data[[col]] = standard_scaler.fit_transform(self.data[[col]])
            
            if col in self.decoders and "outliers" in self.decoders[col]:
                outlier_scaler = self.decoders[col]["outliers"]
                self.decoders[col] = {
                    "encoder": [outlier_scaler, standard_scaler]
                }
            else:
                self.decoders[col] = {"encoder": standard_scaler}


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
    

    def _text_features(self, col):
        '''
        summary: Text 데이터 타입에 대해서는 
        
        '''
        self.data.drop(columns=[col], inplace=True)


    def process_features(self, strategy="mean"):
        '''
        summary: 모든 열에 대해 전처리를 수행합니다.

        return: 
            pd.DataFrame: 전처리가 완료된 데이터프레임.
        '''
        original_columns = list(self.data.columns)
        
        for col in original_columns:
            self.handle_missing_values(col, strategy)
            self.remove_outliers(col)
            processed_df = self.process_column(col)
            
        return processed_df


    def decode(self, df, cols, round_decimals=2):
        '''
        summary: 데이터 전처리 과정에서 변환된 값을 원래 값으로 복원합니다.
        '''
        print('\n ====================Decoding list확인======================== \n')
        print(f'{self.decoders}')
        print('\n ====================Decoding list확인======================== \n')

        for col in cols:
            if col not in self.decoders:
                continue

            feature = self.data_info[col]
            feature_type = feature['type']
            encoder_info = self.decoders[col]
            
            if (feature_type == 'Categorical') or (feature_type == 'Boolean'):
                encoder = encoder_info['encoder']
                df[col] = encoder.inverse_transform(df[col])
            
            elif feature_type == 'Numeric':
                encoder = encoder_info['encoder']
                # Numeric 변환기 처리: 리스트 형태이면 여러 변환기가 적용된 경우
                if isinstance(encoder, list):
                    if len(encoder) == 3:
                        # 저장된 순서: [outlier_scaler, power_transformer, standard_scaler]
                        outlier_scaler, power_transformer, standard_scaler = encoder
                        inv = standard_scaler.inverse_transform(df[[col]])
                        inv = power_transformer.inverse_transform(inv)
                        inv = outlier_scaler.inverse_transform(inv)
                    elif len(encoder) == 2:
                        # 저장된 순서: [power_transformer, standard_scaler]
                        power_transformer, standard_scaler = encoder
                        inv = standard_scaler.inverse_transform(df[[col]])
                        inv = power_transformer.inverse_transform(inv)
                    else:
                        raise ValueError("Unexpected encoder list length for numeric feature.")
                    df[[col]] = np.round(inv, round_decimals)
                else:
                    standard_scaler = encoder
                    inv = standard_scaler.inverse_transform(df[[col]])
                    df[[col]] = np.round(inv, round_decimals)

            elif feature_type == 'DateTime':
                year_col, month_col, day_col = encoder_info['columns']
                df[col] = pd.to_datetime(
                    df[[year_col, month_col, day_col]].astype(str).agg('-'.join, axis=1),
                    errors='coerce'
                )
                # 변환된 연, 월, 일 컬럼 삭제
                df.drop(columns=encoder_info['columns'], inplace=True)

        return df


def preprocessing(data, config_path):
    config = OmegaConf.load(config_path)
    preprocessor = DataPreprocessor(data, config)
    preprocessed_df = preprocessor.process_features()

    return preprocessed_df, preprocessor