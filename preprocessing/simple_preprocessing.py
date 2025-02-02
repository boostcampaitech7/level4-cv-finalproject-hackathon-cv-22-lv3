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


