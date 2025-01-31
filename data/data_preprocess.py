import pandas as pd
import numpy as np
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

    def remove_outliers(self, columns, z_thresh=3):
        '''
        summary: 지정된 열에서 z-score를 기준으로 이상치를 제거합니다.

        args: 
            columns (list): 이상치를 제거할 열 이름 목록.
            z_thresh (float): z-score 임계값. 기본값은 3입니다.
        
        return: 
            pd.DataFrame: 이상치가 제거된 데이터프레임.
        '''
        for col in columns:
            feature = self.data_info[col]
            if feature["type"] == "Numeric":
                z_scores = (self.data[col] - feature["mean"]) / feature["std"]
                self.data = self.data[np.abs(z_scores) <= z_thresh]
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
        summary: 각 열의 특성(type, n_distinct)을 기반으로 적절한 전처리를 수행합니다.

        args:
            col (str): 처리할 열 이름.

        return:
            pd.DataFrame: 전처리가 완료된 데이터프레임.
        '''
        feature = self.data_info[col]
        feature_type = feature['type']

        if feature_type == 'Categorical':
            self._categorical_features(col, feature['n_distinct'])
        
        elif feature_type == 'Numeric':
            self._numeric_features(col, feature['min'], abs(feature['skewness']))
        
        elif feature_type == 'Boolean':
            self._boolean_features(col)
        
        return self.data


    def _categorical_features(self, col, n_distinct):
        '''
        summary: 범주형 변수를 처리하는 함수. 
             고유값 개수(n_distinct)에 따라 OneHotEncoder 또는 LabelEncoder를 적용합니다.

        args:
            col (str): 처리할 열 이름.
            n_distinct (int): 해당 열의 고유값 개수.

        return:
            None: 데이터프레임을 직접 수정하며, 인코더 정보를 self.decoders에 저장합니다.
        '''
        if n_distinct == 1:
            self.data.drop(columns=[col], inplace=True)
            return
        
        if n_distinct <= 2:
            # OneHotEncoder 적용
            ohe = OneHotEncoder(sparse_output=False)
            label = self.data[col].values.reshape(-1, 1)
            one_hot_encoded = ohe.fit_transform(label)
    
            # 새로운 컬럼 이름 생성
            feature_names = ohe.get_feature_names_out([col])

            # 원-핫 인코딩 결과를 DataFrame으로 변환
            one_hot_df = pd.DataFrame(one_hot_encoded, columns=feature_names, index=self.data.index)

            # 기존 컬럼 삭제 후 새로운 데이터프레임 병합
            self.data.drop(columns=[col], inplace=True)
            self.data[feature_names] = one_hot_df
            
            # 인코더 정보 저장
            self.decoders[col] = {
                'encoder': ohe,
                'feature_names' : feature_names
            }

        else:
            # Label Encoding 적용
            le = LabelEncoder()
            self.data[col] = le.fit_transform(self.data[col])
            
            # 인코더 정보 저장
            self.decoders[col] = {
                'encoder': le,
            }

    def _numeric_features(self, col, min_value, skewness):
        '''
        summary: 수치형 변수를 처리하는 함수. 
                데이터의 왜도(skewness)와 최소값(min_value)에 따라 적절한 변환을 적용합니다.

        args:
            col (str): 처리할 열 이름.
            min_value (float): 해당 열의 최소값.
            skewness (float): 해당 열의 왜도 (1 이상이면 비대칭 분포로 간주).

        return:
            None: 데이터프레임을 직접 수정하며, 인코더 정보를 self.decoders에 저장합니다.
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
            self.data[[col]] = transformer.fit_transform(self.data[[col]])
        
        # 항상 MinMaxScaler 적용 (0~1 범위로 정규화)
        min_max_scaler = MinMaxScaler()
        self.data[[col]] = min_max_scaler.fit_transform(self.data[[col]])

        self.decoders[col] = {
            "encoder" : [min_max_scaler, transformer]
        }

    def _boolean_features(self, col):
        '''
        summary: 불리언 변수를 처리하는 함수. 
                True/False 값을 0/1로 변환하기 위해 LabelEncoder를 적용합니다.

        args:
            col (str): 처리할 열 이름.

        return:
            None: 데이터프레임을 직접 수정하며, 인코더 정보를 self.decoders에 저장합니다.
        '''
        le = LabelEncoder()
        self.data[col] = le.fit_transform(self.data[col])
        self.decoders[col] = {
            'encoder': le
        }

    def process_features(self, strategy="mean"):
        '''
        summary: 모든 열에 대해 전처리를 수행합니다.

        return: 
            pd.DataFrame: 전처리가 완료된 데이터프레임.
        '''
        processed_frames = []

        for col in self.data.columns:
            self.handle_missing_values(col, strategy)
            processed_col = self.process_column(col)
            if processed_col is not None:
                processed_frames.append(processed_col)

        # 전처리된 모든 열 병합
        return pd.concat(processed_frames, axis=1)
    

    def decode(self, col):
        '''
        summary: 데이터 전처리 과정에서 변환된 값을 원래 값으로 복원합니다.

        args:
            col (str): 원래 값으로 복원할 열 이름.

        return:
            pd.DataFrame: 디코딩이 완료된 데이터프레임.
        '''
        if col not in self.decoders:
            raise ValueError(f"{col}에 대한 인코더 정보가 없습니다.")

        feature = self.data_info[col]
        feature_type = feature['type']
        n_distinct = feature['n_distinct']

        encoder_info = self.decoders[col]
        encoder = encoder_info['encoder']

        if (feature_type == 'Categorical') and (n_distinct <= 2):
            feature_names = encoder_info['feature_names']
            one_hot_values = self.data[feature_names].values
            original_labels = encoder.inverse_transform(one_hot_values)

            self.data[col] = original_labels.squeeze()
            self.data.drop(columns=feature_names, inplace=True)

        elif (feature_type == 'Categorical' and n_distinct > 2) or (feature_type == 'Boolean'):
            self.data[col] = encoder.inverse_transform(self.data[col])
        
        elif feature_type == 'Numeric':
            min_max_scaler, transfomer = encoder
            self.data[[col]] = min_max_scaler.inverse_transform(self.data[[col]])
            
            if transfomer:
                self.data[[col]] = transfomer.inverse_transform(self.data[[col]])
        
        return self.data


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