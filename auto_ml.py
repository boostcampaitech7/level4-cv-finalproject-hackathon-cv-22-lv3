import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score, f1_score
from autogluon.tabular import TabularPredictor
 
def automl_module(data, task, target, preset, time_to_train):
    train_df, test_df = train_test_split(data, test_size=0.2, random_state=42)
    print(train_df.head())
    
    if target not in train_df.columns:
        raise KeyError(f"Label column '{target}' is missing from training data. Training data columns: {list(train_df.columns)}")


    predictor = TabularPredictor(
        label=target,             
        problem_type=task,
        verbosity=1
    ).fit(
        train_data=train_df,     
        time_limit=time_to_train,          
        presets=preset   
    )

    y_pred = predictor.predict(test_df.drop(columns=[target]))  

    if task == 'regression':
        mae = mean_absolute_error(test_df[target], y_pred)
        r2 = r2_score(test_df[target], y_pred)
        print("AutoGluon Regressor 결과:")
        print(f" - MAE : {mae:.4f}")
        print(f" - R^2 : {r2:.4f}")
    elif task in ['binary', 'multiclass']:
        accuracy = accuracy_score(test_df[target], y_pred)
        f1 = f1_score(test_df[target], y_pred, average='weighted')
        print("AutoGluon Classifier 결과:")
        print(f" - Accuracy : {accuracy:.4f}")
        print(f" - F1 Score : {f1:.4f}")
    else:
        raise ValueError(f"Unsupported task type: {task}")

    leaderboard = predictor.leaderboard(test_df, silent=True)
    print(f'LeaderBoard Result :\n{leaderboard}')


    feature_importance = predictor.feature_importance(test_df)
    print(f'Feature Importance:\n{feature_importance}')
    print('==============================================================\n')

    evaluation = predictor.evaluate(test_df)
    print(f'Evaluation Results:\n{evaluation}')
    print('==============================================================\n')

    return predictor, test_df



def train_model(data, task, target, selected_quality, time_to_train):
    try:
        model, test_df = automl_module(data, task, target, selected_quality, time_to_train)
        # logging.info(f"The Best Model is {model}")
    except Exception as e:
        logging.error(f"Model training failed: {e}")
        return

    return model, test_df