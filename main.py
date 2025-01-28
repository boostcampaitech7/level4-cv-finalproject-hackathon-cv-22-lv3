import pandas as pd
from simple_preprocessing import simple_preprocessing, add_grad_column
from auto_ml import automl_module
from determine_type import determine_problem_type

def main():
    data = pd.read_csv('/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-22-lv3/mat2.csv')
    target = 'grade'
    data = add_grad_column(data)

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

    task = determine_problem_type(data, target)
    data = simple_preprocessing(data,task)

    model = automl_module(data, task, target, selected_quality, time_to_train)
    print(f'The Best Model is {model}')

if __name__ == '__main__':
    main()


