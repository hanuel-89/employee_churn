from datetime import datetime
from apps.core.logger import Logger
import os
import pickle
import shutil

class FileOperation:
    """
    ***************************************************************************
    *
    * filename:         file_operation.py
    * version:          1.0
    * author:           Emmanuel Folorunsho
    * date created:     12-OCT-2022
    *
    * change history:
    *
    * who           when            version       change(include bug# if apply)
    * -------       ---------       ----------    -------------------
    * hanuel89      12-OCT-2022     1.0           Initial creation
    *
    *
    * description:      File operation class
    *
    ***************************************************************************
    """

    def __init__(self, run_id, data_path, mode):
        self.run_id = run_id
        self.data_path = data_path
        self.logger = Logger(self.run_id, 'FileOperation', mode)

    def save_model(self, model, filename):
        """
        Method to save the model file.
        Args:
            model: A trained ML model
            filename: Path to save the model
        Return:
            None (Model is saved in filepath)
        """
        try:
            self.logger.info('Start Saving Model')
            # Create separate directory for each model
            path = os.path.join('apps/models/', filename)
            # Remove previously existing models for each cluster
            # Or make path directory if not exist
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.makedirs(path)
            with open(f'{path}/{filename}.sav', 'wb') as f:
                pickle.dump(model, f) # Save model to file
            self.logger.info(f'Model File {filename} saved')
            self.logger.info('End of save models')
            return 'success'
        except Exception as e:
            self.logger.exception(f'Exception raised while trying to save model: {e}')
            raise e

    def load_model(self, filename):  # sourcery skip: raise-specific-error
        """
        Method to load saved models from file

        Args:
            filename: Path where model is saved
        Returns:
            model: The model saved in filepath
        """
        try:
            self.logger.info('Start loading model')
            with open(f'apps/models/{filename}/{filename}.sav', 'rb') as f:
                self.logger.info(f'Model file {filename} loaded')
                self.logger.info('End of load model')
                return pickle.load(f)
        except Exception as e:
            self.logger.exception(f'Exception raised while loading model: {e}')
            raise Exception() from e

    def correct_model(self, cluster_number):
        # sourcery skip: raise-specific-error
        """
        Method to find the best model

        Args:
            cluster_number(int): Cluster with the best model
        Returns:
            model: The best model file
        """
        try:
            self.logger.info('Start finding the best model')
            self.cluster_number = cluster_number
            self.folder_name = 'apps/models'
            self.list_of_model_files = []
            self.list_of_files = os.listdir(self.folder_name)
            for self.file in self.list_of_files:
                try:
                    if (self.file.index(str(self.cluster_number)) != -1):
                        self.model_name = self.file
                except Exception:
                    continue
            self.model_name = self.model_name.split('.')[0]
            self.logger.info('End of finding the correct model')
            return self.model_name
        except Exception as e:
            self.logger.info(f'Exception raised while finding the correct model{str(e)}')
            raise Exception() from e