import json
from multiprocessing.sharedctypes import Value
from os import listdir
import shutil
from datetime import datetime
import os

import pandas as pd

from apps.database.database_operation import DatabaseOperation
from apps.core.logger import Logger

class LoadValidate:
    """
    ***************************************************************************
    *
    * filename:         load_validate.py
    * version:          1.0
    * author:           Emmanuel Folorunsho
    * date created:     18-OCT-2022
    *
    * change history:
    *
    * who           when            version       change(include bug# if apply)
    * -------       ---------       ----------    -------------------
    * hanuel89      18-OCT-2022     1.0           Initial creation
    *
    *
    * description:      Class to load and validate the dataset
    *
    ***************************************************************************
    """


    def __init__(self, run_id, data_path, mode):
        self.run_id = run_id
        self.data_path = data_path
        self.logger = Logger(self.run_id, self.data_path, mode)


    def values_from_schema(self, schema_file):
        """
        Method to read the schema file

        Args:
            schema_file: The file that contains the schema
        Returns:
            column_name(string): The name of the column
            number_of_columns(int): The number of columns in the schema
        """
        try:
            self.logger.info('Start of reading from schema file')
            with open(f'apps/database/{schema_file}.json', 'r') as f:
                dic = json.load(f)
                f.close()
            column_names = dic['ColName']
            number_of_columns = dic['NumberOfColumns']
            self.logger.info('End of reading from schema')
        except ValueError:
            self.logger.exception('ValueError raised while reading from schema file')
            raise ValueError
        except KeyError:
            self.logger.exception('KeyError raised while reading from schema file')
            raise KeyError
        except Exception as e:
            self.logger.exception(f'Error raised while reading from schema file: {e}')
            raise e
        return column_names, number_of_columns


    def validate_column_length(self, number_of_columns):
        """
        Method to validate the length of the column

        Args:
            number_of_columns(int): The number of columns in the schema file
        Returns:
            None
        """
        try:
            self.logger.info('Start of validating column length')
            for file in listdir(self.data_path):
                csv = pd.read_csv(f'{self.data_path}/{file}')
                if csv.shape[1] != number_of_columns:
                    shutil.move(f'{self.data_path}/{file}', f'{self.data_path}_rejects')
                    self.logger.info('End of validating number of columns')
        except OSError:
            self.logger.exception('OSError raised while validating number of columns')
            raise OSError
        except Exception as e:
            self.logger.exception(f'Error raised while validating number of columns: {e}')
            raise e


    def validate_missing_values(self):
        """
        Method to validate the missing values in a column. It checks if all the values in the column are missing, it moves the csv to a rejects folder

        Args:
            None
        Returns:
            None
        """
        try:
            self.logger.info('Start of validating missing numbers')
            for file in listdir(self.data_path):
                csv = pd.read_csv(f'{self.data_path}/{file}')
                count = 0
                for columns in csv:
                    if (len(csv[columns]) - csv[columns].count()) == len(csv[columns]):
                        count += 1
                        shutil.move(f'{self.data_path}/{file}', f'{self.data_path}_rejects')
                        self.logger.info(f'All missing values in column: {file}')
                        break
            self.logger.info('End of validating missing values')
        except OSError:
            self.logger.exception('OSError raised while validating missing values')
            raise OSError
        except Exception as e:
            self.logger.exception('Error raised while validating missing values')
            raise e


    def replace_missing_values(self):
        """
        Method to replace the missing values in a column with 'NULL'

        Args:
            None
        Returns:
            None
        """

        try:
            self.logger.info('Start of replacing missing values with NULL')
            only_files = list(listdir(self.data_path))
            for file in only_files:
                csv = pd.read_csv(f'{self.data_path}/{file}')
                csv.fillna('NULL', inplace=True)
                csv.to_csv(f'{self.data_path}/{file}', index=None, header=True)
                self.logger.info(f'{file}: File successfully transformed')
            self.logger.info('End of replacing missing values with NULL')
        except Exception as e:
            self.logger.exception(f'Error raised while replacing missing values: {e}')


    def archive_old_files(self):
        """
        Method to archive rejected files

        Args:
            None
        Returns:
            None
        """

        now = datetime.now()
        date = now.date()
        time = now.strftime("%H%M%S")
        try:
            # Archive old rejected files
            self.logger.info('Start of archiving old files')
            source = f'{self.data_path}_rejects/'
            if os.path.isdir(source):
                path = f'{self.data_path}_archive'
                if not os.path.isdir(path):
                    os.makedirs(path)
                dest = f'{path}/reject_{str(date)}_{str(time)}'
                files = os.listdir(source)
                for f in files:
                    if not os.path.isdir(dest):
                        os.makedirs(dest)
                    if f not in os.listdir(dest):
                        shutil.move(source + f, dest)
            self.logger.info('End of archiving old files')

            # Archive old validated files
            self.logger.info('Start of archiving old validated files')
            source = f'{self.data_path}_validation/'
            if os.path.isdir(source):
                path = f'{self.data_path}_archive'
                if not os.path.isdir(path):
                    os.makedirs(path)
                dest = f'{path}/validation_{str(date)}_{str(time)}'
                files = os.listdir(source)
                for f in files:
                    if not os.path.isdir(dest):
                        os.makedirs(dest)
                    if f not in os.listdir(dest):
                        shutil.move(source + f, dest)
            self.logger.info('End of archiving old validated files')

            # Archive old processed files
            self.logger.info('Start of archiving old processed files')
            source = f'{self.data_path}_processed/'
            if os.path.isdir(source):
                path = f'{self.data_path}_archive'
                if not os.path.isdir(path):
                    os.makedirs(path)
                dest = f'{path}/processed_{str(date)}_{str(time)}'
                files = os.listdir(source)
                for f in files:
                    if not os.path.isdir(dest):
                        os.makedirs(dest)
                    if f not in os.listdir(dest):
                        shutil.move(source + f, dest)
            self.logger.info('End of archiving old validated files')



