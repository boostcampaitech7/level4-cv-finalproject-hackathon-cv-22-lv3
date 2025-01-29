import pandas as pd
import numpy as np
from omegaconf import OmegaConf
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, MinMaxScaler, StandardScaler


class DropLowVariance(BaseEstimator, TransformerMixin):
    '''
    summary: 고유값의 개수가 1개인 열을 삭제하는 Transformer 클래스.
    
    args:
        data_info (dict): EDA 결과 딕셔너리. 각 열의 'n_distinct' 정보를 사용.
    '''
    def __init__(self, data_info):
        self.data_info = data_info
        self.cols_to_drop = []

    def fit(self, X, y=None):
        '''
        summary: 'n_distinct'가 1인 열을 식별합니다.

        args:
            X (pd.DataFrame): 입력 데이터프레임.
            y (None): 사용하지 않는 매개변수.

        return:
            self: Transformer 객체 자신을 반환.
        '''
        self.cols_to_drop = [col for col in X.columns if self.data_info[col]['n_distinct'] == 1]
        return self
    
    def transform(self, X):
        '''
        summary: 식별된 열을 데이터프레임에서 삭제합니다.

        args:
            X (pd.DataFrame): 입력 데이터프레임.

        return:
            pd.DataFrame: 지정된 열이 삭제된 데이터프레임.
        '''
        return X.drop(columns=self.cols_to_drop, errors='ignore')
    

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

    def remove_outliers(self, columns, z_thresh=3):
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
            if df[col].dtype in ['int64', 'float64']:
                z_scores = (df[col] - df[col].mean()) / df[col].std()
                df = df[np.abs(z_scores) <= z_thresh]
        return df

    def handle_missing_values(self, df, strategy="mean"):
        '''
        summary: 결측치를 열별로 처리합니다. 결측치 비율에 따라 행 삭제 또는 대체 기법을 적용합니다.

        args: 
            df (pd.DataFrame): 입력 데이터프레임.
            strategy (str): 결측치 처리 방법 ('mean', 'median', 'mode', 'knn').
        
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
                if strategy in ['mean', 'median', 'mode']:
                    # SimpleImputer로 처리
                    if df[col].dtype in ['int64', 'float64']:
                        imputer = SimpleImputer(strategy=strategy)
                    else:
                        # 범주형 데이터는 항상 최빈값으로 처리
                        imputer = SimpleImputer(strategy="most_frequent")
                    df[[col]] = imputer.fit_transform(df[[col]])
                elif strategy == "knn":
                    # KNN Imputer로 처리
                    imputer = KNNImputer(n_neighbors=3)
                    df[[col]] = imputer.fit_transform(df[[col]])
                else:
                    raise ValueError("Invalid strategy. Choose from 'mean', 'median', 'mode', 'knn'.")

        return df

    def process_column(self, col):
        '''
        summary: 각 열의 특성(type, n_distinct)을 기반으로 적절한 전처리를 수행합니다.

        args:
            col (str): 처리할 열 이름.

        return:
            pd.DataFrame: 전처리가 완료된 데이터프레임.
        '''
        feature = self.data_info[col]
        feature_type = feature['type']

        if feature_type == 'Categorical':
            n_distinct = feature['n_distinct']

            if n_distinct == 1:
                # 고유값이 1개인 열은 삭제
                return None

            elif n_distinct <= 2:
                # 원-핫 인코딩 적용
                ohe = OneHotEncoder(sparse_output=False)
                encoded = ohe.fit_transform(self.data[[col]])
                feature_names = ohe.get_feature_names_out([col])
                encoded_df = pd.DataFrame(encoded, columns=feature_names, index=self.data.index)
                return encoded_df

            else:
                # 라벨 인코딩 적용
                le = LabelEncoder()
                self.data[col] = le.fit_transform(self.data[col])
                return self.data[[col]]

        elif feature_type == 'Numeric':
            # 수치형 데이터 스케일링
            scaler = StandardScaler()
            self.data[col] = scaler.fit_transform(self.data[[col]])
            return self.data[[col]]

        elif feature_type == 'Boolean':
            # Boolean 데이터 라벨 인코딩
            le = LabelEncoder()
            self.data[col] = le.fit_transform(self.data[col])
            return self.data[[col]]

        else:
            return self.data[[col]]

    def process_features(self):
        '''
        summary: 모든 열에 대해 전처리를 수행합니다.

        return: 
            pd.DataFrame: 전처리가 완료된 데이터프레임.
        '''
        processed_frames = []

        for col in self.data.columns:
            processed_col = self.process_column(col)
            if processed_col is not None:
                processed_frames.append(processed_col)

        # 전처리된 모든 열 병합
        return pd.concat(processed_frames, axis=1)


if __name__ == "__main__":
    # CSV 파일 로드
    df = pd.read_csv("/data/ephemeral/home/data/mat2.csv")
    print("초기 데이터 정보:")
    print(df.info())

    # 데이터 EDA 정보를 JSON에서 로드
    data_info = OmegaConf.load('/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-22-lv3/eda/student_math/filtered_result.json')

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
    processed_df = preprocessor.process_features()

    # 처리 결과 출력
    print("처리 후 데이터 정보:")
    print(processed_df.info())
    print(processed_df.head())