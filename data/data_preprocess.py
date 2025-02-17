import numpy as np
import pandas as pd
from datetime import datetime
from omegaconf import OmegaConf
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.preprocessing import (
    RobustScaler,
    LabelEncoder,
    StandardScaler,
    PowerTransformer,
)


class DataPreprocessor:
    """
    Class for data preprocessing. This class handles outlier removal,
    missing value imputation, and feature-specific processing.
    """

    def __init__(self, df, config):
        """
        Parameters
            df : pd.DataFrame
                The original dataset.
            config : dict or OmegaConf
                Configuration containing preprocessing information, such as filtered_data.
        """
        self.data = df
        self.data_info = config["filtered_data"]
        self.decoders = {}

    def remove_outliers(self, col):
        """
        Remove outliers in the specified column based on the interquartile range.

        Parameters
            col : str
                Name of the column to process.

        Returns
            pd.DataFrame
                DataFrame with outliers handled.
        """
        feature = self.data_info[col]
        if feature["type"] == "Numeric":
            kurtosis = feature["kurtosis"]
            if kurtosis > 3:
                robust_scaler = RobustScaler()
                self.data[[col]] = robust_scaler.fit_transform(self.data[[col]])
                self.decoders[col] = {"outliers": robust_scaler}
        return self.data

    def handle_missing_values(self, col, strategy="mean"):
        """
        Handle missing values in the specified column.

        Parameters
            col : str
                Name of the column.
            strategy : str, optional
                Strategy for imputation ('mean', 'median', 'mode', 'knn'),
                by default "mean".

        Returns
            pd.DataFrame
                DataFrame with missing values handled.
        """
        feature = self.data_info[col]
        missing_ratio = feature["p_missing"]
        if missing_ratio < 0.03:
            self.data = self.data.dropna(subset=[col])
        else:
            if strategy in ["mean", "median", "mode"]:
                if feature["type"] == "Numeric":
                    imputer = SimpleImputer(strategy=strategy)
                else:
                    imputer = SimpleImputer(strategy="most_frequent")
            elif strategy == "knn":
                imputer = KNNImputer(n_neighbors=3)
            else:
                raise ValueError(
                    "Invalid strategy. Choose from 'mean', 'median', 'mode', 'knn'."
                )
            self.data[[col]] = imputer.fit_transform(self.data[[col]])
        return self.data

    def process_column(self, col):
        """
        Process the specified column based on its type.

        Parameters
            col : str
                Name of the column to process.

        Returns
            pd.DataFrame
                DataFrame with the processed column.
        """
        feature = self.data_info[col]
        feature_type = feature["type"]

        if feature_type in ["Categorical", "Boolean"]:
            self._categorical_features(col)
        elif feature_type == "Numeric":
            self._numeric_features(col)
        elif feature_type == "DateTime":
            self._date_features(col)
        elif feature_type == "Text":
            self._text_features(col)

        return self.data

    def _categorical_features(self, col):
        """
        Process a categorical column using label encoding.

        Parameters
            col : str
                Name of the column.
        """
        if not np.issubdtype(self.data[col].dtype, np.integer):
            le = LabelEncoder()
            self.data[col] = le.fit_transform(self.data[col])
            self.decoders[col] = {"encoder": le}

    def _numeric_features(self, col):
        """
        Process a numeric column by handling skewness and scaling.

        Parameters       
            col : str
                Name of the column.
        """
        skewness = abs(self.data_info[col]["skewness"])
        if skewness >= 1:
            power_transformer = PowerTransformer(method="yeo-johnson")
            transformed = power_transformer.fit_transform(self.data[[col]])
            standard_scaler = StandardScaler()
            self.data[[col]] = standard_scaler.fit_transform(transformed)
            if col in self.decoders and "outliers" in self.decoders[col]:
                outlier_scaler = self.decoders[col]["outliers"]
                self.decoders[col] = {
                    "encoder": [outlier_scaler, power_transformer, standard_scaler]
                }
            else:
                self.decoders[col] = {"encoder": [power_transformer, standard_scaler]}
        else:
            standard_scaler = StandardScaler()
            self.data[[col]] = standard_scaler.fit_transform(self.data[[col]])
            if col in self.decoders and "outliers" in self.decoders[col]:
                outlier_scaler = self.decoders[col]["outliers"]
                self.decoders[col] = {"encoder": [outlier_scaler, standard_scaler]}
            else:
                self.decoders[col] = {"encoder": standard_scaler}

    def _date_features(self, col):
        """
        Convert a DateTime column into separate numeric features for year, month, and day.

        Parameters
            col : str
                Name of the DateTime column.
        """
        current_year = datetime.now().year
        self.data[col] = pd.to_datetime(self.data[col], errors="coerce")
        self.data[f"{col}_year"] = self.data[col].dt.year.fillna(current_year).astype(int)
        self.data[f"{col}_month"] = self.data[col].dt.month.fillna(1).astype(int)
        self.data[f"{col}_day"] = self.data[col].dt.day.fillna(1).astype(int)
        self.data.drop(columns=[col], inplace=True)
        self.decoders[col] = {"columns": [f"{col}_year", f"{col}_month", f"{col}_day"]}

    def _text_features(self, col):
        """
        Drop text columns from the dataset.

        Parameters
            col : str
                Name of the text column.
        """
        self.data.drop(columns=[col], inplace=True)

    def process_features(self, strategy="mean"):
        """
        Process all features in the dataset.

        Parameters
            strategy : str, optional
                Strategy for handling missing values, by default "mean".

        Returns
            pd.DataFrame
                The preprocessed DataFrame.
        """
        original_columns = list(self.data.columns)
        for col in original_columns:
            self.handle_missing_values(col, strategy)
            self.remove_outliers(col)
            self.process_column(col)
        return self.data

    def decode(self, df, cols, round_decimals=2):
        """
        Decode processed features back to their original representation.

        Parameters
            df : pd.DataFrame
                DataFrame to be decoded.
            cols : list
                List of columns to decode.
            round_decimals : int, optional
                Number of decimals to round numeric features to, by default 2.

        Returns
            pd.DataFrame
                Decoded DataFrame.
        """
        for col in cols:
            if col not in self.decoders:
                continue

            feature = self.data_info[col]
            feature_type = feature["type"]
            encoder_info = self.decoders[col]

            if feature_type in ["Categorical", "Boolean"]:
                encoder = encoder_info["encoder"]
                df[col] = encoder.inverse_transform(df[col])
            elif feature_type == "Numeric":
                encoder = encoder_info["encoder"]
                if isinstance(encoder, list):
                    if len(encoder) == 3:
                        outlier_scaler, power_transformer, standard_scaler = encoder
                        inv = standard_scaler.inverse_transform(df[[col]])
                        inv = power_transformer.inverse_transform(inv)
                        inv = outlier_scaler.inverse_transform(inv)
                    elif len(encoder) == 2:
                        power_transformer, standard_scaler = encoder
                        inv = standard_scaler.inverse_transform(df[[col]])
                        inv = power_transformer.inverse_transform(inv)
                    else:
                        raise ValueError("Unexpected encoder list length for numeric feature.")
                    df[[col]] = np.round(inv, round_decimals)
                else:
                    standard_scaler = encoder
                    inv = standard_scaler.inverse_transform(df[[col]])
                    df[[col]] = np.round(inv, round_decimals)
            elif feature_type == "DateTime":
                year_col, month_col, day_col = encoder_info["columns"]
                df[col] = pd.to_datetime(
                    df[[year_col, month_col, day_col]].astype(str).agg("-".join, axis=1),
                    errors="coerce"
                )
                df.drop(columns=encoder_info["columns"], inplace=True)
        return df


def preprocessing(data, config_path):
    """
    Preprocess the dataset based on configuration settings.

    Parameters
        data : pd.DataFrame
            The input dataset.
        config_path : str
            Path to the configuration file.

    Returns
        tuple
            A tuple containing:
            - preprocessed_df (pd.DataFrame): The preprocessed DataFrame.
            - preprocessor (DataPreprocessor): The preprocessor object.
    """
    config = OmegaConf.load(config_path)
    preprocessor = DataPreprocessor(data, config)
    preprocessed_df = preprocessor.process_features()
    return preprocessed_df, preprocessor