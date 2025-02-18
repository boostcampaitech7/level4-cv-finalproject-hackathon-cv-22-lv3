from datetime import datetime
import numpy as np
import pandas as pd
from omegaconf import OmegaConf
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.preprocessing import LabelEncoder, PowerTransformer, RobustScaler, StandardScaler
from typing import Tuple


class DataPreprocessor:
    '''
    Summary: 
        데이터 전처리를 위한 클래스.
        이상치 처리, 결측치 처리, 변수 특성별 처리를 수행합니다.
        Numeric, Categorical, Boolean, DateTime, Text 변수 타입별로 적절한 변환을 적용.
    
    Args:
        df (pd.DataFrame): 원본 데이터.
        config (dict): 전처리 정보를 포함한 설정파일.
    
    Attributes:
        data (pd.DataFrame): 전처리가 진행되는 데이터프레임.
        data_info (dict): 열별 전처리 정보를 저장한 딕셔너리.
        decoders (dict): 변환된 데이터를 복원할 때 사용되는 인코더 정보.

    '''
    def __init__(self, df: pd.DataFrame, config: dict):
        self.data = df
        self.data_info = config["filtered_data"]
        self.decoders = {}

    def remove_outliers(self, col: str) -> pd.DataFrame:
        '''
        Summary: 
            첨도(Kurtosis)를 기준으로 이상치를 처리.
            첨도 값이 3보다 큰 경우, RobustScaler를 적용하여 이상치 영향을 줄임.
            이상치 제거가 아니라, 이상치 영향을 줄이는 방향으로 처리됨.

        Args: 
            cols (str): 이상치를 제거할 열 이름.

        Returns: 
            pd.DataFrame: 이상치가 정규화된 데이터프레임.
        '''
        feature = self.data_info[col]

        if feature["type"] == "Numeric":
            kurtosis = feature["kurtosis"]
            
            if kurtosis > 3:
                robust_scaler = RobustScaler()
                
                self.data[[col]] = robust_scaler.fit_transform(self.data[[col]])

                self.decoders[col] = {"outliers" : robust_scaler}

        return self.data

    def handle_missing_values(self, col: str, strategy: str = "mean") -> pd.DataFrame:
        '''
        Summary: 
            결측치를 열별로 처리.
            결측치 비율에 따라 행 삭제 또는 대체 기법을 적용.

        Args: 
            df (pd.DataFrame): 입력 데이터프레임.
            strategy (str): 결측치 처리 방법 ('mean', 'median', 'mode', 'knn').
        
        Returns: 
            pd.DataFrame: 결측치가 처리된 데이터프레임.
        '''
        feature = self.data_info[col]
        missing_ratio = feature["p_missing"]            
    
        if missing_ratio < 0.03:
            self.data = self.data.dropna(subset=[col])
        else:
            if strategy in ['mean', 'median', 'mode']:
                if feature["type"] == "Numeric":
                    imputer = SimpleImputer(strategy=strategy)
                else:
                    imputer = SimpleImputer(strategy="most_frequent")
            elif strategy == "knn":
                imputer = KNNImputer(n_neighbors=3)
            else:
                raise ValueError("Invalid strategy. Choose from 'mean', 'median', 'mode', 'knn'.")
            
            self.data[[col]] = imputer.fit_transform(self.data[[col]])
        
        return self.data

    def process_column(self, col: str) -> pd.DataFrame:
        '''
        Summary: 
            각 열의 특성(type)에 따라 적절한 전처리를 수행.

        Args:
            col (str): 처리할 열 이름.

        Returns:
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

    def _categorical_features(self, col: str):
        '''
        Summary: 
            범주형 변수를 Label Encoding 방식으로 변환하는 함수
            범주형 변수의 값이 숫자가 아닌 경우, LabelEncoder를 적용하여 변환함.

        Args:
            col (str): 처리할 열 이름.

        Returns:
            None: 데이터프레임을 직접 수정하며, 변환된 스케일러 정보를 self.decoders에 저장함.
        '''
        if not np.issubdtype(self.data[col].dtype, np.integer):
            le = LabelEncoder()
            self.data[col] = le.fit_transform(self.data[col])
            
            self.decoders[col] = {'encoder': le}

            return None

    def _numeric_features(self, col: str):
        '''
        Summary: 
            수치형 변수를 변환하여 정규성을 확보하는 함수
            절대값 왜도 1이상이면 PowerTransformer 적용하여 분포를 정규화
        
        Args: 
            col (str): 처리할 열 이름

        Returns:
            None: 데이터프레임을 직접 수정하며, 변환된 스케일러 정보를 self.decoders에 저장함.
        '''
        skewness = abs(self.data_info[col]['skewness'])
        
        if skewness >= 1:
            power_transformer = PowerTransformer(method='yeo-johnson', standardize=True)
            self.data[[col]] = power_transformer.fit_transform(self.data[[col]])
            
            if col in self.decoders and "outliers" in self.decoders[col]:
                outlier_scaler = self.decoders[col]["outliers"]
                self.decoders[col] = {"encoder": [outlier_scaler, power_transformer]}
            else:
                self.decoders[col] = {"encoder": power_transformer}
        else:
            standard_scaler = StandardScaler()
            self.data[[col]] = standard_scaler.fit_transform(self.data[[col]])
            
            if col in self.decoders and "outliers" in self.decoders[col]:
                outlier_scaler = self.decoders[col]["outliers"]
                self.decoders[col] = {"encoder": [outlier_scaler, standard_scaler]}
            else:
                self.decoders[col] = {"encoder": standard_scaler}

    def _date_features(self, col: str):
        '''
        Summary: 
            날짜 데이터를 년/월/일로 변환하는 함수.
            원본 DateTime 컬럼을 3개(Date_Year, Date_Month, Date_Day)로 분리.

        Args: 
            col (str): 처리할 열 이름.

        Returns:
            None: 데이터프레임을 직접 수정하며, 변환된 날짜 정보를 self.decoders에 저장함.
        '''        
        current_year = datetime.now().year
        
        self.data[col] = pd.to_datetime(self.data[col], errors='coerce')

        self.data[f'{col}_year'] = self.data[col].dt.year.fillna(current_year).astype(int)
        self.data[f'{col}_month'] = self.data[col].dt.month.fillna(1).astype(int)
        self.data[f'{col}_day'] = self.data[col].dt.day.fillna(1).astype(int)
        self.data.drop(columns=[col], inplace=True)
        
        self.decoders[col] = {'columns': [f'{col}_year', f'{col}_month', f'{col}_day']}
    
    def _text_features(self, col: str):
        '''
        Summary: 
            텍스트 데이터를 처리하는 함수.
            삭제하는 방식으로 처리됨.

        Args: 
            col (str): 처리할 열 이름.

        Returns:
            None: 텍스트 데이터 컬럼을 삭제함.
        '''
        self.data.drop(columns=[col], inplace=True)

    def process_features(self, strategy: str = "mean") -> pd.DataFrame:
        '''
        Summary: 
            데이터의 모든 열에 대해 전처리를 수행하는 함수.
            결측치 처리, 이상치 변환, 데이터 변환을 수행.

        Args:
            strategy (str): 결측치 처리 방법 ('mean', 'median', 'mode', 'knn').
        
        Returns: 
            pd.DataFrame: 전처리가 완료된 데이터프레임.
        '''
        original_columns = list(self.data.columns)
        
        for col in original_columns:
            self.handle_missing_values(col, strategy)
            self.remove_outliers(col)
            processed_df = self.process_column(col)
            
        return processed_df

    def decode(self, df: pd.DataFrame, cols: list, round_decimals: int = 2) -> pd.DataFrame:
        '''
        Summary: 
            데이터 전처리 과정에서 변환된 값을 원래 값으로 복원하는 함수.
        
        Args:
            df (pd.DataFrame): 복원할 데이터프레임.
            cols (list): 복원할 열 목록.
            round_decimals (int): 수치형 데이터 복원 시 반올림할 소수점 자릿수 (기본값 2)
        
        Returns:
            pd.DataFrame: 원래 값으로 복원된 데이터프레임
        '''
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
                if isinstance(encoder, list):
                        outlier_scaler, scaler = encoder
                        inv = scaler.inverse_transform(df[[col]])
                        inv = outlier_scaler.inverse_transform(inv)
                        df[[col]] = np.round(inv, round_decimals)
                else:
                    scaler = encoder
                    inv = scaler.inverse_transform(df[[col]])
                    df[[col]] = np.round(inv, round_decimals)

            elif feature_type == 'DateTime':
                year_col, month_col, day_col = encoder_info['columns']
                df[col] = pd.to_datetime(
                    df[[year_col, month_col, day_col]].astype(str).agg('-'.join, axis=1),
                    errors='coerce'
                )
                df.drop(columns=encoder_info['columns'], inplace=True)

        return df


def preprocessing(data: pd.DataFrame, config_path: str) -> Tuple[pd.DataFrame, DataPreprocessor]:
    '''
    Summary:
        데이터를 전처리하고 전처리 객체를 반환하는 함수.
        설정 파일을 로드하여 DataPreprocessor 객체를 생성.
        데이터에 대해 결측치 처리, 이상치 변환, 변수 변환 등을 수행
    
    Args:
        data (pd.DataFrame): 전처리를 수행할 원본 데이터.
        config_path (str): 설정 파일(.yaml 또는 .json)의 경로.

    Returns:
        Tuple[pd.DataFrame, DataPreprocessor]:
        전처리가 완료된 데이터프레임.
        데이터 전처리 객체(DataPreprocessor), 후처리 시 활용 가능.
    '''
    config = OmegaConf.load(config_path)
    preprocessor = DataPreprocessor(data, config)
    preprocessed_df = preprocessor.process_features()

    return preprocessed_df, preprocessor