import argparse
from utils.logger_config import logger


def get_config_by_argparser():
    '''
    Summary:
        내부 테스트를 위해 실행 시 데이터 파일 경로(`data_path`)와 설정(`config`)을 선택하는 함수.
        argparse를 사용하여 실행 시 입력값을 받을 수 있도록 구성됨.
        
        사용자는 `--data_path` 옵션을 통해 데이터 파일 경로를 지정하고,  
        `--config` 옵션을 통해 사용할 설정을 선택할 수 있음.
    
    Args:
        없음 (이 함수는 인자값을 받지 않음)
    
    Returns:
        Tuple[str, dict, dict]: 
            data_path (str): 데이터 파일 경로
            process_2_config (dict): `process_2` 설정
            process_3_config (dict): `process_3` 설정
    '''
    parser = argparse.ArgumentParser(description="Process 2 & 3 Config Selector")
    parser.add_argument("--data_path", type=str, required=True, help="데이터 파일 경로를 입력하세요.")
    parser.add_argument("--config", type=str, choices=["02", "22"], required=True, help="설정을 선택하세요: 02 또는 22")
    
    args = parser.parse_args()

    if args.config == "02":
        process_2_config = {
            "target_feature": "Price",
            "controllable_feature": ["Longtitude", "Lattitude", "BuildingArea"],
            "necessary_feature": [],
            "limited_feature": 4,
            "model": {"time_to_train": 30, "model_quality": "best"},
        }
        
        process_3_config = {
            "optimization": {
                "direction": "maximize",
                "n_trials": 10,
                "target_class": 0,
                "opt_range": {
                    "Longtitude": [20, 20],
                    "Lattitude": [20, 20],
                    "BuildingArea": [20, 20],
                },
            }
        }
    elif args.config == "22":
        process_2_config = {
            "target_feature": "Attrition",
            "controllable_feature": ["MonthlyIncome", "WorkLifeBalance"],
            "necessary_feature": ["Age", "Education", "DistanceFromHome", "OverTime"],
            "limited_feature": 10,
            "model": {"time_to_train": 100, "model_quality": "best"},
        }
        process_3_config = {
            "optimization": {
                "direction": "maximize",
                "n_trials": 15,
                "target_class": 0,
                "opt_range": {
                    "MonthlyIncome": [20, 20],
                    "WorkLifeBalance": [0, 3],
                },
            }
        }
    else:
        return None, None
    
    logger.info(f"📂 데이터 파일 경로: {args.data_path}")
    logger.info(f"✅ '{args.config}' 설정이 선택되었습니다!")

    return args.data_path, process_2_config, process_3_config