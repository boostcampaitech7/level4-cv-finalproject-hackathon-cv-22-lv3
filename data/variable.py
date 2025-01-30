import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, MinMaxScaler, StandardScaler, PowerTransformer
from sklearn.impute import SimpleImputer, KNNImputer

class DataPreprocessor:
    '''
    summary: 데이터 전처리를 위한 클래스. 이상치 처리, 결측치 처리, 변수 특성별 처리를 수행합니다.
    '''
    def __init__(self, df, data_info, scaling_method="standard"):
        '''
        args:
            df (pd.DataFrame): 원본 데이터.
            data_info (dict): 각 열의 전처리 정보를 담은 딕셔너리.
            scaling_method (str): 'standard' 또는 'minmax' 중 선택해 스케일링 방식을 설정합니다.
        '''
        self.data = df
        self.data_info = data_info
        self.scaling_method = scaling_method
        self.label_encoders = {}  # Label Encoder 저장 (디코딩용)
        self.scalers = {}  # 스케일러 저장 (디코딩용)
    
    def remove_outliers(self, df, columns, z_thresh=3):
        '''
        summary: 지정된 열에서 z-score를 기준으로 이상치를 제거합니다.
        '''
        for col in columns:
            if df[col].dtype in ['int64', 'float64']:
                z_scores = (df[col] - df[col].mean()) / df[col].std()
                df = df[np.abs(z_scores) <= z_thresh]
        return df

    def handle_missing_values(self, df, strategy="mean"):
        '''
        summary: 결측치를 열별로 처리합니다. 결측치 비율에 따라 행 삭제 또는 대체 기법을 적용합니다.
        '''
        for col in df.columns:
            feature = self.data_info[col]
            missing_ratio = feature["p_missing"]            
            if missing_ratio < 0.03:
                df = df.dropna(subset=[col])  # 결측치 비율이 3% 미만이면 행 삭제
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
                
                df[[col]] = imputer.fit_transform(df[[col]])
        return df

    def process_features(self, df, cfg):
        '''
        summary: 범주형 변수는 라벨 인코딩, 수치형 변수는 스케일링을 수행합니다.
        args: 
            df (pd.DataFrame): 입력 데이터프레임.
            cfg (dict): 컬럼별 데이터 정보 (컬럼 타입, 왜도 등 포함).
        return: 
            pd.DataFrame: 처리된 데이터프레임.
        '''
        for col in df.columns:
            feature = cfg[col]
            feature_type = feature['type']

            if feature_type == 'Categorical':
                self._categorical_features(df, col, feature['n_distinct'])
            
            elif feature_type == 'Numeric':
                self._numeric_features(df, col, feature['min'], abs(feature['skewness']))
            
            elif feature_type == 'Boolean':
                self._boolean_features(df, col)
        
        return df

    def _categorical_features(self, df, col, n_distinct):
        '''
        summary: 범주형 변수 처리 (OneHotEncoder 또는 LabelEncoder).
        '''
        if n_distinct == 1:
            df.drop(columns=[col], inplace=True)
            return
        
        if n_distinct <= 2:
            # OneHotEncoder 적용
            ohe = OneHotEncoder(sparse_output=False)
            label = df[col].values.reshape(-1, 1)
            one_hot_encoded = ohe.fit_transform(label)
    
            # 새로운 컬럼 이름 생성
            feature_names = ohe.get_feature_names_out([col])

            # 원-핫 인코딩 결과를 DataFrame으로 변환
            one_hot_df = pd.DataFrame(one_hot_encoded, columns=feature_names, index=df.index)

            # 기존 컬럼 삭제 후 새로운 데이터프레임 병합
            df.drop(columns=[col], inplace=True)
            df[feature_names] = one_hot_df
        else:
            # Label Encoding 적용
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
            self.label_encoders[col] = le  # Label Encoder 저장 (디코딩용)

    def _numeric_features(self, df, col, min_value, skewness):
        '''
        summary: 수치형 변수 처리 (Box-Cox, Yeo-Johnson, StandardScaler, MinMaxScaler).
        '''
        transformer = None

        if skewness >= 1:
            if min_value <= 0:
                transformer = PowerTransformer(method='yeo-johnson')
            else:
                transformer = PowerTransformer(method='box-cox')

        elif skewness < 0.5:
            transformer = StandardScaler()

        if transformer:
            df[[col]] = transformer.fit_transform(df[[col]])
            self.scalers[col] = transformer  # 스케일러 저장 (디코딩용)
        
        # 항상 MinMaxScaler 적용 (0~1 범위로 정규화)
        min_max_scaler = MinMaxScaler()
        df[[col]] = min_max_scaler.fit_transform(df[[col]])
        self.scalers[col] = min_max_scaler  # MinMaxScaler도 저장 (디코딩용)

    def _boolean_features(self, df, col):
        '''
        summary: 불리언 변수 처리 (Label Encoding 적용).
        '''
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        self.label_encoders[col] = le  # 저장 (디코딩용)

    # 디코딩 함수 
    def inverse_transform():
        pass