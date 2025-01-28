

def identify_categorical_features(data, threshold=10):
    """
    고유 값의 수가 threshold 이하인 피처를 카테고리형으로 식별합니다.
    
    Parameters:
        data (pd.DataFrame): 데이터프레임
        threshold (int): 고유 값의 최대 수
        
    Returns:
        list: 카테고리형 피처 리스트
    """
    categorical_features = [col for col in data.columns if data[col].nunique() <= threshold]
    print('\n\n')
    print(f"\nCategorical Features Identified: {categorical_features}")
    print('\n\n')

    return categorical_features
