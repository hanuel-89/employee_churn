import json
from symbol import test_nocond

from sklearn.model_selection import train_test_split

from apps.core.logger import Logger
from apps.core.file_operation import FileOperation
from apps.ingestion.load_validate import LoadValidate
from apps.tuning.model_tuner import  ModelTuner
from apps.preprocess.preprocessor import Preprocessor
from apps.tuning.cluster import KMeansCluster


class TrainModel:
    """
    ***************************************************************************
    *
    * filename:         train_model.py
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
    * description:      Model training class
    *
    ***************************************************************************
    """

    def __init__(self, run_id, data_path):
        self.run_id = run_id
        self.data_path = data_path
        self.logger = Logger(self.run_id, 'TrainModel', 'training')
        self.loadValidate = LoadValidate(self.run_id, self.data_path,'training')
        self.preProcess = Preprocessor(self.run_id, self.data_path,'training')
        self.modelTuner = ModelTuner(self.run_id, self.data_path, 'training')
        self.fileOperation = FileOperation(self.run_id, self.data_path, 'training')
        self.cluster = KMeansCluster(self.run_id, self.data_path)

    def training_model(self):
        """
        Method to train the model

        Args:
            None
        Returns:
            None
        """
        try:

            self.logger.info('----- Start of Training Process -----')
            self.logger.info(f'Run_ID: {self.run_id}')
            # Load, validate, and tranform the training dataset
            self.loadValidate.validate_trainset()
            # Training data preprocessing activities
            self.X, self.y = self.Preprocessor.preprocess_trainset()
            columns = {'data_columns': list(self.X.columns)}
            with open('apps/database/columns.json', 'w') as f:
                f.write(json.dumps(columns))
            # Create the clusters
            number_of_clusters = self.cluster.elbow_plot(self.X)
            # Divide the data into clusters
            self.X = self.cluster.create_clusters(self.X, number_of_clusters)
            # Create a new column in the dattaset with the corresponding cluster assignment
            self.X['Labels'] = self.y
            # Get the unique cluster from the dataset
            cluster_list = self.X['Cluster'].unique()
            # Parse all the cluster and find the best ML algorithm that fits each cluster
            for i in cluster_list:
                cluster_data = self.X[self.X['Cluster'] == i] # Filter the data for one cluster
                # Prepare the feature and target columns
                cluster_features = cluster_data.drop(['Labels', 'Cluster'], axis=1)
                cluster_label = cluster_data['Labels']

                # Split the data into training and testing dataset
                X_train, X_test, y_train, y_test = train_test_split(cluster_features, cluster_label, test_size=0.2, random_state=44, stratify=cluster_label)

                # Get the best model for each cluster
                best_model_name, best_model = self.modelTuner.get_best_model(X_train, y_train, X_test, y_test)

                # Save the best model to the model directory
                save_model = self.fileOperation.save_model(best_model, best_model_name + str(i))

            self.logger.info('----- End of Training Process -----')
        except Exception as e:
            self.logger.exception(f'Error raised while training the model: {e}')
            raise e

