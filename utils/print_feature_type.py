import pandas as pd  


def print_features_with_types(features, categorical_features, title):
    """
    피처의 이름, 타입, 값을 체계적으로 출력하는 함수입니다.
    
    Parameters:
        features (pd.Series or dict): 피처 이름과 값
        categorical_features (list): 카테고리형 피처 리스트
        title (str): 출력 제목
    """
    print(f"\n{title}")
    print("-" * len(title))
    for feature, value in features.items():
        ftype = 'Categorical' if feature in categorical_features else 'Numerical'
        print(f" - {feature} ({ftype}): {value}")
    print()


def compare_features(original_features, optimized_features, categorical_features):
    """
    원본 피처와 최적화된 피처를 비교하여 출력하는 함수입니다.
    
    Parameters:
        original_features (pd.Series or dict): 원본 피처 이름과 값
        optimized_features (pd.Series or dict): 최적화된 피처 이름과 값
        categorical_features (list): 카테고리형 피처 리스트
    """
    comparison_df = pd.DataFrame({
        'Feature': original_features.index,
        'Type': ['Categorical' if feat in categorical_features else 'Numerical' for feat in original_features.index],
        'Original': original_features.values,
        '->' : '->',
        'Optimized': optimized_features.values
    })
    
    print("\nFeature Comparison:")
    print(comparison_df.to_string(index=False))
    print()