from datetime import datetime
import random

class Config:
    """
    ***************************************************************************
    *
    * filename:         config.py
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
    * description:      Configuration class for instance attributes
    *
    ***************************************************************************
    """

    def __init__(self) -> None:
        self.training_data_path = 'data/training_data'
        self.training_database = 'training'
        self.prediction_data_path = 'data/prediction_data'
        self.prediction_database = 'prediction'

    def get_run_id(self):
        """
        Method to generate the run ID
        Args:
            None
        Returns:
            string: run ID
        """
        self.now = datetime.now()
        self.date = self.now.date()
        self.current_time = self.now.strftime("%H%M%S")
        return f'{str(self.date)}_{str(self.current_time)}_{random.randint(100000000, 999999999)}'