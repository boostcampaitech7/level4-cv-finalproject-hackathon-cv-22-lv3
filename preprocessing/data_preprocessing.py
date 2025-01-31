from determine_feature import determine_problem_type, auto_determine_fixed_features
from simple_preprocessing import simple_preprocessing, add_grad_column
import logging

def base_preprocessing(config, data, target):
    """데이터를 통해서 기본적으로 ( target 값,  (min,max)값, target의 클래스, 기본적인 전처리를 진행합니다.)

    Args:
        config (dict): 설정 정보를 담고 있는 딕셔너리 
        data (pd.DataFrame): 불러온 데이터 ㅡ레임
        target (_type_): 최적화 하고자 하는 Feature

    Returns:
        task(str): 어떤 task를 진행할지
        data(pd.DataFrame): 기본 전처리가 진행된 데이터셋
        direction(str) : Minimize OR Maximize
        target_class(str) : 최적화 할 class가 어떤 종류인지
    """
    try:
        task = determine_problem_type(data, target)
        data = simple_preprocessing(data, task)
        logging.info(f"Problem type determined: {task}")
    except Exception as e:
        logging.error(f"Failed to determine problem type or preprocess data: {e}")
        return

    direction = config.get('direction', 'maximize')
    if direction not in ['minimize', 'maximize']:
        logging.error("Invalid direction. Please choose 'minimize' or 'maximize'.")
        return
    target_class = config.get('target_class', '') 

    return task, data, direction, target_class
