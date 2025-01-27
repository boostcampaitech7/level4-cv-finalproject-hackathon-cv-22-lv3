import pandas as pd
from simple_preprocessing import simple_preprocessing, add_grad_column
from auto_ml import automl_module
from determine_type import determine_problem_type

def main():
    data = pd.read_csv('/data/ephemeral/home/kagglehub/datasets/henryshan/student-performance-prediction/versions/2/mat2.csv')
    target = 'grade'
    data = add_grad_column(data)

    task = determine_problem_type(data, target)
    data = simple_preprocessing(data,task)

    model = automl_module(data, task, target)
    print(f'The Best Model is {model}')

if __name__ == '__main__':
    main()


