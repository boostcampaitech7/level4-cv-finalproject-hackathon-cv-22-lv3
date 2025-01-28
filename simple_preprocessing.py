import pandas as pd 
import numpy as np
from sklearn.preprocessing import LabelEncoder



def add_grad_column(data):
    conditions =[
        data['G3'] < 15,
        data['G3'].isin([16,17,18]),
        data['G3'].isin([19,20])
    ]

    choice = ['C','B','A']
    print('regression 문제를 multi classification으로 변경하였습니다.')
    data['grade'] = np.select(conditions, choice, default='C')
    return data



def simple_preprocessing(data, task):
    label_encoder = LabelEncoder()
    object_columns = data.select_dtypes(include=['object','bool']).columns.tolist()

    for column in object_columns:
        data[column] = label_encoder.fit_transform(data[column])

        mapping_df = pd.DataFrame({
            'original_value': label_encoder.classes_,
            'encoded_value': range(len(label_encoder.classes_))
        })
        # print(f"Mapping for {column}:\n", mapping_df)

    data.head(10)

    data = data.drop(['Unnamed: 0'], axis='columns')

    return data
    
