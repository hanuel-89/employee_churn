import json
import pandas as pd
import numpy as np

from sklearn.impute import KNNImputer

from apps.core.logger import Logger

class Preprocessor:
    """
    ***************************************************************************
    *
    * filename:         preprocessor.py
    * version:          1.0
    * author:           Emmanuel Folorunsho
    * date created:     20-OCT-2022
    *
    * change history:
    *
    * who           when            version       change(include bug# if apply)
    * -------       ---------       ----------    -------------------
    * hanuel89      20-OCT-2022     1.0           Initial creation
    *
    *
    * description:      Configuration class for instance attributes
    *
    ***************************************************************************
    """

    def __init__(self, run_id, data_path, mode):
        self.run_id = run_id
        self.data_path = data_path
        self.logger = Logger(self.run_id, 'Preprocessor', mode)

    def get_data(self):
        """
        Method to fetch the data to be preprocessed

        Args:
            None
        Returns:
            None
        """
        try:
            self.logger.info('Start: Reading the dataset')
            self.data = pd.read_csv(f'{self.data_path}_validation/InputFile.csv')
            self.logger.info('End: Reading the dataset')
        except Exception as e:
            self.logger.info(f'Error raised while reading the dataset: {e}')
            raise e

    def drop_columns(self, data, columns):
        """
        Method to drop columns from the dataset

        Args:
            data(dataframe): A pandas DataFrame of the dataset
            columns(string): The name of the column(s) to be dropped
        Returns:
            A dataframe with some removed columns
        """

        self.data = data
        self.columns = columns
        try:
            self.logger.info('Start: Removing unwanted columns from the dataframe')
            # Drop the specified columns
            self.required_data = self.data.drop(labels=self.columns, axis=1)
            self.logger.info('End: Removing unwanted columns from the dataframe')
            return self.required_data
        except Exception as e:
            self.logger.info(f'Error raised while dropping columns from the dataset: {e}')
            raise e

    def is_null_present(self, data):
        """
        Method to check if there are nulls in the dataset

        Args:
            data(dataframe): A pandas DataFrame of the dataset
        Returns:
            boolean: A true value if null values are present
        """

        self.null_present = False
        try:
            self.logger.info('Start: Checking for null values')
            self.count_null = data.isna().sum() # Count the number of nulls in each column
            for i in self.count_null:
                if i > 0:
                    self.null_present = True
                    break
            # If there are null values, log them in a new dataframe
            if(self.null_present):
                df_with_null_values = pd.DataFrame()
                df_with_null_values['columns'] = data.columns
                df_with_null_values['count_missing_values'] = np.asarray(data.isna().sum())
                df_with_null_values.to_csv(f'{self.data_path}_validation/null_values.csv') # Save the df to CSV
            self.logger.info('End: Checking for null values')
        except Exception as e:
            self.logger.info(f'Error raised while cheking for null values: {e}')
            raise e

    def impute_missing_values(self, data):
        """
        Method to impute missing values

        Args:
            data: A pandas df of the dataset
        Returns
            New dataframe without missing values
        """

        self.data = data
        try:
            self.logger.info('Start: Imputing the missing data')
            imputer = KNNImputer(n_neighbors=3, weights='uniform', missing_values=np.nan) # Instantiate an imputer
            self.new_array = imputer.fit_transform(self.data) # Impute the missing values

            # Put the new array in a dataframe
            self.new_data = pd.DataFrame(data=self.new_array, columns=self.data.columns)
            self.logger.info('End: Imputing the missing data')
            return self.new_data
        except Exception as e:
            self.logger.info(f'Error raised while imputing missing values: {e}')
            raise e

    def feature_encoding(self, data):
        """
        Method to encode the features in the dataset

        Args:
            data: A pandas of the dataset
        Returns:
            new_data: A pandas df with encoded features
        """

        self.data = data
        try:
            self.logger.info('Start: Encoding features')
            # Copy columns that are type 'object' into new_data
            self.new_data = data.select_dtypes(include=['object']).copy()

            # Use pd.get_dummies method to encode the new dataset
            for col in self.new_data.columns:
                self.new_data = pd.get_dummies(self.new_data, columns=[col], prefix=[col], drop_first=True)
            self.logger.info('End: Encoding features')
            return self.new_data
        except Exception as e:
            self.logger.info(f'Error raised while encoding features: {e}')
            raise e

    def split_features_label(self, data, label_name):
        """
        Method to split dataset into features and label

        Args:
            data: A pandas dataframe of the dataset
        Returns:
            features, labels
        """

        self.data = data

        try:
            self.logger.info('Start: Splitting data into features & labels')
            self.y = self.data[label_name] # Get the label
            self.X = self.data.drop(label_name, axis=1) # Get the features
            self.logger.info('End: Splitting data into features & labels')
            return self.X, self.y
        except Exception as e:
            self.logger.info(f'Error raised while splitting in features & labels: {e}')
            raise e


    def final_predictset(self, data):
        """
        Method to build final predict set by adding additional encoded column with value as 0

        Args:
            data: A pandas dataframe of the dataset
        Returns:
            column_names(string): The names of the columns in the dataset
            number_of_columns(int): The number of columns in the dataset
        """

        try:
            self.logger.info('Start: Building final predict set')
            with open('apps/database/columns.json', 'r') as f:
                data_columns = json.load(f)['data_columns']
                f.close()
            df = pd.DataFrame(data=None, columns=data_columns)
            df_new = pd.concat([df, data], ignore_index=True, sort=False)
            data_new = df_new.fillna(0) # Fill the missing values with 0
            self.logger.info('End: Building final predict set')
        except ValueError:
            self.logger.exception('ValueError raised while building final predictset')
            raise ValueError
        except KeyError:
            self.logger.exception('KeyError raised while building final predictset')
            raise KeyError
        except Exception as e:
            self.logger.exception(f'Exception raised while building final predictset:{e}')
            raise e

    def preprocess_trainset(self):
        """
        Method to preprocess the training data

        Args:
            None
        Returns:
            None
        """

        try:
            self.logger.info('Start: Preprocessing the training data')
            data = self.get_data() # Get data in df
            data = self.drop_columns(data, ['empid']) # Drop unwanted columns
            cat_df = self.feature_encoding(data) # Encode categorical columns

            # Concatenate the encoded column with original dataset
            data = pd.concat([cat_df, data], axis=1)

            # Drop the original encoded 'salary' column
            data = self.drop_columns(data, ['salary'])

            is_null_present = self.is_null_present(data) # Check for nulls

            # Impute missing values if null
            if (is_null_present):
                data = self.impute_missing_values(data)
            # Split into features and labels
            self.X, self.y = self.split_features_label(data, label_name='left')
            self.logger.info('End: Preprocessing the training data')
            return self.X, self.y
        except Exception as e:
            self.logger.exception(f'Exception raised while preprocessing training data: {e}')

    def preprocess_predictset(self):
        """
        Method to preprocess the prediction data

        Args:
            None
        Returns:
            None
        """

        try:
            self.logger.info('Start: Preprocessing the prediction data')
            data = self.get_data() # Get data in df
            # data = self.drop_columns(data, ['empid']) # Drop unwanted columns
            cat_df = self.feature_encoding(data) # Encode categorical columns

            # Concatenate the encoded column with original dataset
            data = pd.concat([cat_df, data], axis=1)

            # Drop the original encoded 'salary' column
            data = self.drop_columns(data, ['salary'])

            is_null_present = self.is_null_present(data) # Check for nulls

            # Impute missing values if null
            if (is_null_present):
                data = self.impute_missing_values(data)

            data = self.final_predictset(data)
            self.logger.info('End: Preprocessing the training data')
            return data
        except Exception as e:
            self.logger.exception(f'Exception raised while preprocessing training data: {e}')


    def preprocess_predict(self, data):
        """
        Method to preprocess the prediction data

        Args:
            None
        Returns:
            None
        """

        try:
            self.logger.info('Start: Preprocessing the prediction data')
            cat_df = self.feature_encoding(data) # Encode categorical columns

            # Concatenate the encoded column with original dataset
            data = pd.concat([cat_df, data], axis=1)

            # Drop the original encoded 'salary' column
            data = self.drop_columns(data, ['salary'])

            is_null_present = self.is_null_present(data) # Check for nulls

            # Impute missing values if null
            if (is_null_present):
                data = self.impute_missing_values(data)

            data = self.final_predictset(data)
            self.logger.info('End: Preprocessing the training data')
            return data
        except Exception as e:
            self.logger.exception(f'Exception raised while preprocessing training data: {e}')