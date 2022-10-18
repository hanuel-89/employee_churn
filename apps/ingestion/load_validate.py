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
        Method to validate the missing values

        Args:
            None
        Returns:
            None
        """


