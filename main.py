from process.process import process_1, process_2, process_3
from utils.user_setting import get_config_by_argparser

def main():
    '''
    Summary:
        내부 테스트를 위해 전체 ML 파이프라인을 실행하는 함수.
        `get_config_by_argparser()`를 통해 `data_path`, `process_2_config`, `process_3_config`을 받아 실행됨.

    Args:
        없음 (이 함수는 직접 인자를 받지 않고 `get_config_by_argparser()`를 통해 설정값을 가져옴)

    Returns:
        str: 최종적으로 업데이트된 `user_config_path`
    '''
    data_path, process_2_config, process_3_config = get_config_by_argparser()

    model_config_path, user_config_path, original_df = process_1(data_path)

    model_config_path, user_config_path, model, preprocessed_df, preprocessor = process_2(model_config_path, user_config_path, original_df, process_2_config)

    user_config_path = process_3(model_config_path, user_config_path, model, preprocessed_df, preprocessor, process_3_config)

    return user_config_path


if __name__ == "__main__":
    final_user_config_path = main()