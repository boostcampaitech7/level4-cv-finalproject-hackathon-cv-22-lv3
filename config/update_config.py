import os.path as osp
import json
import logging
from datetime import datetime
from omegaconf import OmegaConf

def update_config(config_path, config_updates, user=False):
    '''
    '''
    try:
        config = OmegaConf.load(config_path)
        logging.info(f"설정 파일 로드 완료 : {config_path}")
    except FileNotFoundError:
        logging.warning(f"파일을 찾을 수 없습니다.")
    
    updated_config = OmegaConf.merge(config, OmegaConf.create(config_updates))

    if user:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")        
        save_path = osp.dirname(config_path)
        user_config_filename = f"{timestamp}_user_config.json"
        user_config_path = osp.join(save_path, user_config_filename)

        with open(user_config_path, 'w', encoding='utf-8') as f:
            json.dump(OmegaConf.to_container(updated_config, resolve=True), f, indent=4, ensure_ascii=False)
        
        logging.info(f"사용자 설정 업데이트 완료 : {config_path}")
    else:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(OmegaConf.to_container(updated_config, resolve=True), f, indent=4, ensure_ascii=False)
        
        logging.info(f"모델 설정 업데이트 완료 : {config_path}")

    return config_path

if __name__ == "__main__":
    config_path = '/data/ephemeral/home/uploads/model_config.json'
    config_updates = {
        "target_feature": "test",
        "controllabel_feature": "test",
        "necessary_feature": "test",
        "limited_feature" : "test",
        }
    
    update_config = update_config(config_path, config_updates)