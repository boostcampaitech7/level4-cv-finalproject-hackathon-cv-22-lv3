import yaml
import argparse
import os
import logging


def load_config(config_path='config.yaml'):
    """
    YAML 형식의 구성 파일을 로드합니다.

    Parameters:
    - config_path (str): 구성 파일의 경로.

    Returns:
    - config (dict): 구성 설정을 담은 딕셔너리.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")
    
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    return config

def parse_arguments():
    """
    명령줄 인자를 파싱합니다.

    Returns:
    - args (Namespace): 파싱된 인자들을 담은 Namespace 객체.
    """
    parser = argparse.ArgumentParser(description='Machine Learning Project Configuration')
    parser.add_argument('--config', type=str, default='config.yaml',
                        help='Path to the configuration YAML file (default: config.yaml)')
    return parser.parse_args()