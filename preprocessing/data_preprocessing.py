from determine_feature import determine_problem_type, auto_determine_fixed_features
from simple_preprocessing import simple_preprocessing, add_grad_column
import logging

def base_preprocessing(config, data, target):
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
