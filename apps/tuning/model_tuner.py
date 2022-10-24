from sklearn.metrics import r2_score
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, accuracy_score

from xgboost import XGBClassifier

from apps.core.logger import Logger

class ModelTuner:
    """
    ***************************************************************************
    *
    * filename:         model_tuner.py
    * version:          1.0
    * author:           Emmanuel Folorunsho
    * date created:     24-OCT-2022
    *
    * change history:
    *
    * who           when            version       change(include bug# if apply)
    * -------       ---------       ----------    -------------------
    * hanuel89      24-OCT-2022     1.0           Initial creation
    *
    *
    * description:      Class to create and tune models
    *
    ***************************************************************************
    """

    def __init__(self, run_id, data_path, mode):
        self.run_id = run_id
        self.data_path = data_path
        self.logger = Logger(self.run_id, 'ModelTuner', mode)
        self.rfc = RandomForestClassifier(random_state=44)
        self.xgb = XGBClassifier(objective='binary:logistic', random_state=44)

    def best_params_randomforest(self, X_train, y_train):
        """
        Method to get the best params of a RFC

        Args:
            X_train: The training features
            y_train: The training labels
        Returns:
            best_model: A tuned RFC model
        """
        try:
            self.logger.info('Start: Finding best RFC params')
            # Declare a parameter grid
            self.param_grid = {"n_estimators": [10, 50, 100, 130], "criterion": ['gini', 'entropy'], "max_depth": range(2, 4), "max_features": ['auto', 'log2']}

            # Initialize a grid search object
            self.grid = GridSearchCV(estimator=self.rfc, param_grid=self.param_grid, cv=5)
            # Fit data to grid
            self.grid.fit(X_train, y_train)
            # Extract the best parameters from the grid
            self.criterion = self.grid.best_params_['criterion']
            self.max_depth = self.grid.best_params_['max_depth']
            self.max_features = self.grid.best_params_['max_features']
            self.n_estimators = self.grid.best_params_['n_estimators']

            # Create a model with the best parameters
            self.rfc = RandomForestClassifier(n_estimators=self.n_estimators, criterion=self.criterion, max_depth=self.max_depth, max_features=self.max_features, random_state=44)

            # Train the new model
            self.rfc.fit(X_train, y_train)
            self.logger.info(f'The params of the tuned model are: {str(self.grid.best_params_)}')
            self.logger.info('End: Finding best RFC params')

            return self.rfc # Return the tuned RFC model
        except Exception as e:
            self.logger.exception(f'Exception raised while finding the best rfc parameters: {e}')
            raise e


    def best_params_xgboost(self, X_train, y_train):
        """
        Method to get the best params of a XGBC

        Args:
            X_train: The training features
            y_train: The training labels
        Returns:
            best_model: A tuned XGBC model
        """
        try:
            self.logger.info('Start: Finding best XGBC params')
            # Declare a parameter grid
            self.param_grid = {
                'learning_rate': [0.5, 0.1, 0.01, 0.001],
                'max_depth': [3, 5, 10, 20],
                'n_estimators': [10, 50, 100, 200]
            }

            # Initialize a grid search object
            self.grid = GridSearchCV(estimator=self.xgb, param_grid=self.param_grid, cv=5)
            # Fit data to grid
            self.grid.fit(X_train, y_train)
            # Extract the best parameters from the grid
            self.learning_rate = self.grid.best_params_['learning_rate']
            self.max_depth = self.grid.best_params_['max_depth']
            self.n_estimators = self.grid.best_params_['n_estimators']

            # Create a model with the best parameters
            self.rfc = XGBClassifier(objective='binary:logistic', n_estimators=self.n_estimators, learning_rate=self.learning_rate, max_depth=self.max_depth, random_state=44)

            # Train the new model
            self.xgb.fit(X_train, y_train)
            self.logger.info(f'The params of the tuned XGBC model are: {str(self.grid.best_params_)}')
            self.logger.info('End: Finding best XGBC params')

            return self.rfc # Return the tuned RFC model
        except Exception as e:
            self.logger.exception(f'Exception raised while finding the best xgb parameters: {e}')
            raise e


    def get_best_model(self, X_train, y_train, X_test, y_test):
        """
        Method to get the best model i.e RFC or XGB

        Args:
            X_train: The traniing features
            y_train: The training labels
            X_test: The testing features
            y_test: The testing label
        Returns:
            The model with the best score
        """
        try:
            self.logger.info('Start: Finding the best model')
            # Get XGBC Scores
            # Initialize a tuned XGB model
            self.xgboost = self.best_params_xgboost(X_train, y_train)
            # Use the XGBC to predict the test set
            self.xgboost_pred = self.xgboost.predict(X_test)

            if len(y_test.unique()) == 1: # Use accuracy_score metric if there is only one (1) class in the prediction dataser
                self.xgboost_score = accuracy_score(y_test, self.xgboost_pred)
                self.logger.info(f'The accuracy of the XGB model is: {self.xgboost_score}')
            else:
                self.xgboost_score = roc_auc_score(y_test, self.xgboost_pred)
                self.logger.info(f'AUC for the XGB model is: {self.xgboost_score}')

            # Get RFC Scores
            # Initialize a tuned RFC model
            self.rfc = self.best_params_randomforest(X_train, y_train)
            # Use the rfc model to predict the test set
            self.rfc_pred = self.rfc.predict(X_test)

            if len(y_test.unique()) == 1: # Use accuracy_score metric if there is only one (1) class in the prediction dataser, else use roc_auc_score if there is more than one (1) class
                self.rfc_score = accuracy_score(y_test, self.rfc_pred)
                self.logger.info(f'The accuracy of the RFC model is: {self.rfc_score}')
            else:
                self.rfc_score = roc_auc_score(y_test, self.rfc_pred)
                self.logger.info(f'AUC for the RFC model is: {self.rfc_score}')
            self.logger.info('End: Finding the best model')


            # Compare the two models (RFC & XGB)
            if (self.rfc_score > self.xgboost_score):
                return 'RFC', self.rfc
            else:
                return 'XGBC', self.xgboost
        except Exception as e:
            self.logger.info(f'Exception raised while finding the best model: {e}')
            raise e









