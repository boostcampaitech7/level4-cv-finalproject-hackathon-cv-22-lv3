def base_optimize_setting(merged_file_path, task):
    print('\n\n ======= 현재는 최적화 세팅 화면 입니다. =======')

    if task != 'regression':
        target_class = input('최적화하고 싶은 Feature의 클래스를 선택해주세요 : ')
        direction = 'maximize'
    else:
        target_class = None
        while True:
            direction = input('Target Feature를 최소/최소화할지 고르세요 (minimize | maximize) : ').strip().lower()
            if direction in ['minimize', 'maximize']:
                break
            else:
                print("잘못된 입력입니다. 'minimize' 또는 'maximize'를 입력해주세요.")
    
    n_trials = int(input('최적화를 시도할 횟수를 선택하세요 : '))
    return direction, n_trials, target_class