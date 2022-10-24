from apps.core.logger import Logger
from apps.core.file_operation import FileOperation
from apps.tuning.model_tuner import ModelTuner
from apps.ingestion.load_validate import LoadValidate
from apps.preprocess.preprocessor import Preprocessor

from sklearn.model_selection import  train_test_split
from sklearn.cluster import KMeans
from kneed import  KneeLocator

import matplotlib.pyplot as plt

class KMeansCluster:
    """
    ***************************************************************************
    *
    * filename:         cluster.py
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
    * description:      Class to cluster the dataset
    *
    ***************************************************************************
    """

    def __init__(self, run_id, data_path):
        self.run_id = run_id
        self.data_path = data_path
        self.logger = Logger(self.run_id, 'KMeansCluster', 'traning')
        self.fileOperation = FileOperation(self.run_id, self.data_path, 'training')


    def elbow_plot(self, data):
        """
        Method to save the plot to decide the optimum number of clusters of the file.

        Args:
            data: The data to be clustered
        Returns:
            knee(int): The optimum number of clusters
        """
        # Declare an empty 'within cluster sum of errors' list
        wcss = []
        cluster_range = range(1, 11)
        try:
            self.logger.info('Start: Elbow plot')
            for i in cluster_range:
                # Initialize a kmeans object
                kmeans = KMeans(n_clusters=i, init='k-means++', random_state=44)
                kmeans.fit(data) # Fit the data to KMeans object
                wcss.append(kmeans.inertia_)
            # Plot graph of wcss against the number of clusters
            plt.plot(cluster_range, wcss)
            plt.title('Rainbow Plot')
            plt.xlabel('Number of Clusters')
            plt.ylabel('WCSS')
            # Save the plot to local folder
            plt.savefig('apps/models/kmeans_elbow.png')
            # Find the optimum number of clusters
            self.kn = KneeLocator(cluster_range, wcss, curve='convex', direction='decreasing')
            self.logger.info(f'The optimum number of clusters is: {str(self.kn.knee)}')
            self.logger.info('End: Elbow plot')
            return self.kn.knee
        except Exception as e:
            self.logger.exception(f'Exception raised while plotting elbow: {e}')
            raise e


    def create_clusters(self, data, number_of_clusters):
        """
        Method to create the optimum cluster

        Args:
            data: The data to be clustered
            number_of_clusters(int): The optimum number of clusters
        Returns:
            dataframe: A pandas df with cluster columns
        """
        self.data = data
        try:
            self.logger.info('Start: Creating clusters')
            # Initiate a KMeans object
            self.kmeans = KMeans(n_clusters=number_of_clusters, init='k-means++', random_state=44)
            self.y_kmeans = self.kmeans.fit_predict(data) # Cluster ther data
            self.saveModel = self.fileOperation.save_model(self.kmeans, 'KMeans') # Save the model to a directory
            self.data['Cluster'] = self.y_kmeans # Create a new column showing the cluster number in the dataset
            self.logger.info(f'Successfully created {str(self.kn.knee)} clusters')
            self.logger.info('End: Creating clusters')
        except Exception as e:
            self.logger.exception(f'Exception raised while creating clusters: {e}')
            raise e






