import pandas as pd
from omegaconf import OmegaConf
from data.data_preprocess import DataPreprocessor
from utils.determine_feature import categorical_feature
from optimization.auto_ml import train_model
from optimization.feature_optimization import feature_optimize

# 원본 데이터프레임
original_df = pd.read_csv('/data/ephemeral/home/data/WA_Fn-UseC_-HR-Employee-Attrition.csv')
# 테스트할 설정 파일
test_config = OmegaConf.load('/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-22-lv3/test_optim/config/test_config.json')
# 테스트 설정 파일 경로
test_config_path = '/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-22-lv3/test_optim/config/test_config.json'

# 원본 데이터 프레임 전처리
data_preprocess = DataPreprocessor(original_df, test_config)

# 타겟 변수
target_var = test_config['target_feature']
print(f'타겟 변수 : {target_var}')

# 제어 변수
controllable_var = test_config['controllable_feature']
print(f'제어 변수 : {controllable_var}')

# 전처리 진행할 컬럼들 (현재 모든 열에 대해서 전처리를 진행합니다.)
pre_process_cols = list(original_df.columns)
print(f'전처리 진행할 변수 : {pre_process_cols}')

#데이터 전처리
preprocessed_df = data_preprocess.process_features()
print(f'\n 전처리 결과 : \n{preprocessed_df.head()}')

# config에 맞춘 학습 진행
model, test_df = train_model(preprocessed_df, test_config)

categorical_features = categorical_feature(preprocessed_df, test_config_path)

# 최적화 인자값 설정
task = test_config['model']['task']
config = test_config
env_feature = test_config['Added_feature']
for col in controllable_var:
    env_feature.remove(col)

# 데이터프레임 디코딩
test_df = data_preprocess.decode(preprocessed_df, controllable_var)

comparison_df, original_prediction, optimized_prediction_value = feature_optimize(
    preprocessed_df, task, config, test_df,
    model, categorical_features, env_feature)
