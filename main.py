import pandas as pd
from simple_preprocessing import simple_preprocessing, add_grad_column
from auto_ml import automl_module
from determine_type import determine_problem_type
from optimization import optimize_features
from sklearn.model_selection import train_test_split
from utils.print_feature_type import print_features_with_types, compare_features
from utils.analysis_feature import identify_categorical_features


def main():
    data = pd.read_csv('/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-22-lv3/mat2.csv')
    target = 'G3'
    # data = add_grad_column(data)

    quality_map = {
    0: "best_quality",
    1: "high_quality",
    2: "good_quality",
    3: "medium_quality"
    }
    print('0 : best_quality \n 1 : high_quality \n 2 : good_quality \n 3 : medium_quality')
    preset = int(input('Select the model accuarcy : '))  
    selected_quality = quality_map.get(preset, "Invalid selection")
    print(f"Selected quality: {selected_quality}")

    time_to_train = int(input('Enter the amount of time to train the model : ')) 
    n_trials = int(input('Enter the optimization search time'))

    task = determine_problem_type(data, target)
    data = simple_preprocessing(data,task)

    model, test_df = automl_module(data, task, target, selected_quality, time_to_train)
    print(f'The Best Model is {model}')

    # 카테고리형 피처 식별
    categorical_features = identify_categorical_features(data, threshold=10)


    # 고정할 피처 정의 ( 여기서 고정해야하는 feature를 이제 동적으로 관리해야한다. )
    fixed_features = ['G1', 'G2', 'absences']
    print(f"\nFixed Features (Not to be optimized): {fixed_features}")


    # 피처 최적화 수행
    print("\n ============ Starting feature optimization to maximize the target variable... ============")
    
    # 변경가능한 feature들 설정 ( 고정된 feature들을 제외한 feature들 )
    feature_columns = data.drop(columns=[target]).columns.tolist()
    features_to_optimize = [feat for feat in feature_columns if feat not in fixed_features]



    # 피처의 최소값과 최대값을 자동으로 설정 ( 일단은 각 feature의 최대 최소를 범위로 제한한다. )
    feature_bounds = {}
    for feature in features_to_optimize:
        min_val = data[feature].min()
        max_val = data[feature].max()
        feature_bounds[feature] = (min_val, max_val)
    


    # 최적화할 샘플 선택 (여기서는 테스트 데이터셋의 첫 번째 샘플)
    sample_idx = 0
    original_sample = test_df.iloc[sample_idx].drop(labels=[target])
    # print_features_with_types(original_sample, categorical_features, "Original Sample")

 
    
    # 최적화 실행 ( classification의 경우 target으로 하는 class를 설정해주어야한다.) 
    # 하지만 regression의 경우 따로 사용하진 않는다.
    optimized_features, optimized_prediction = optimize_features(
        predictor=model, 
        original_features=original_sample, 
        feature_bounds=feature_bounds, 
        categorical_features=categorical_features,
        task='multiclass',
        direction='maximize',  # 또는 'minimize'
        n_trials=100,
        target_class='A'  # 'desired_class'는 모델의 클래스 레이블 중 하나
    )
        
    # print_features_with_types(optimized_features, categorical_features, "Optimized Features")
    compare_features(original_sample, pd.Series(optimized_features), categorical_features)

    optimized_sample = optimized_features.copy()
    for feature in fixed_features:
        if feature in original_sample:
            optimized_sample[feature] = original_sample[feature]
        else:
            print(f"Warning: Fixed feature '{feature}' not found in original sample.")


    # 최적화 값과 원본 값을 비교한다.
    original_prediction_series = model.predict(pd.DataFrame([original_sample.to_dict()]))
    optimized_prediction_series = model.predict(pd.DataFrame([optimized_features]))
    

    try:
        original_prediction = original_prediction_series.iloc[0]
    except KeyError:
        original_prediction = original_prediction_series.values[0]
    
    try:
        optimized_prediction_value = optimized_prediction_series.iloc[0]
    except KeyError:
        optimized_prediction_value = optimized_prediction_series.values[0]
    
    print(f"\nOriginal Prediction: {original_prediction}")
    print(f"Optimized Prediction: {optimized_prediction_value}")
    

if __name__ == '__main__':
    main()