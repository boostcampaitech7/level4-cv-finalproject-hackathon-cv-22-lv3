def identify_categorical_features(filtered_data: dict) -> list:
    """
    Identify categorical and boolean features from the filtered EDA data.

    Parameters
        filtered_data : dict
            A dictionary where each key is a column name and the corresponding value is a 
            dictionary containing column information, including a 'type' key.

    Returns
        list
            A list of column names for which the type is either 'Categorical' or 'Boolean'.
    """
    categorical_features = []
    for column_name, column_info in filtered_data.items():
        if isinstance(column_info, dict) and (
            column_info.get("type") == "Categorical" or column_info.get("type") == "Boolean"
        ):
            categorical_features.append(column_name)
    return categorical_features