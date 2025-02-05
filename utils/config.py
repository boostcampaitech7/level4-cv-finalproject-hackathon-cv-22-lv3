import json
import argparse
import os
import logging

def load_config(config_path='config.json'):
    """
    JSON 형식의 구성 파일을 로드합니다.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")
    
    with open(config_path, 'r', encoding="utf-8") as file:
        config = json.load(file)
    
    return config


def parse_arguments():
    parser = argparse.ArgumentParser(description='Machine Learning Project Configuration')
    parser.add_argument('--config', type=str, default='config.json',
                        help='Path to the configuration JSON file (default: config.json)')
    return parser.parse_args()