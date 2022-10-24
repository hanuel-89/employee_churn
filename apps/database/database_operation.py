import sqlite3
import csv
from os import  listdir
import shutil
import os

from apps.core.logger import  Logger

class DataBaseOperation:
    """
    ***************************************************************************
    *
    * filename:         database_operation.py
    * version:          1.0
    * author:           Emmanuel Folorunsho
    * date created:     17-OCT-2022
    *
    * change history:
    *
    * who           when            version       change(include bug# if apply)
    * -------       ---------       ----------    -------------------
    * hanuel89      17-OCT-2022     1.0           Initial creation
    *
    *
    * description:      Class to handle database operations
    *
    ***************************************************************************
    """

    def __init__(self, run_id, data_path, mode):
        self.run_id = run_id
        self.data_path = data_path
        self.logger = Logger(self.run_id, 'DatabaseOperation', mode)

    def database_connection(self, database_name):
        """
        Method to initiate connection to the database

        Args:
            database_name(string): The name of the database
        Returns:
            Connection to the SQLite DB
        """
        try:
            conn = sqlite3.connect(f'apps/database/{database_name}.db')
            self.logger.info(f'Opened {database_name} successfully')
        except ConnectionError:
            self.logger.info(f'Error while connecting to db: {ConnectionError}')
        return conn

    def create_table(self, database_name, table_name, column_names):
        # sourcery skip: avoid-builtin-shadow
        """
        Method to create database tables

        Args:
            database_name (string): Name of the database
            table_name (string): Name of the table
            column_tables (string): Column names of the table
        Returns:
            None
        """
        try:
            self.logger.info('Start creting table')
            conn = self.database_connection(database_name)

            if (database_name == 'prediction'):
                conn.execute("DROP TABLE IF EXISTS '" + table_name + "';")

            c = conn.cursor()
            c.execute("SELECT count(name) FROM sqlite_master WHERE type = 'table' AND name = '" + table_name + "'")
            if c.fetchone()[0] == 1:
                conn.close()
                self.logger.info('Tables created successfully')
                self.logger.info(f'Database {database_name} successfully closed')
            else:
                for key in column_names.keys():
                    type = column_names[key]
                    # Check if table exists and and the columns
                    try:
                        conn.execute(f"ALTER TABLE {table_name}" + " ADD COLUMN {column_name} {dataType}".format(column_name=key, dataType=type))

                        self.logger.info(f"ALTER TABLE {table_name} ADD COLUMN")
                    except Exception as e:
                        conn.execute(f"CREATE TABLE  {table_name}" + " ({column_name} {dataType})".format(column_name=key, dataType=type))

                        self.logger.info(f"CREATE TABLE {table_name} column_name")
                conn.close()
            self.logger.info("End of creating table")
        except Exception as e:
            self.logger.exception(f'Exception raised while Creating Table: {e}')
            raise e

    def insert_data(self, database_name, table_name):
        """
        Method to insert data into table in the database

        Args:
            database_name: The name of the database
            table_name: Tne name of the table
        Returns:
            None
        """
        conn = self.database_connection(database_name)
        good_data_path = self.data_path
        bad_data_path = f'{self.data_path}_rejects'
        only_files = list(listdir(good_data_path))
        self.logger.info('Start of inserting data into table...')
        for file in only_files:
            try:
                with open(f'{good_data_path}/{file}', 'r') as f:
                    next(f)
                    reader = csv.reader(f, delimiter=',')
                    for line in enumerate (reader):
                        to_db = ''
                        for list_ in line[1]:
                            try:
                                to_db = f'{to_db},{list_}' + "'"
                            except Exception as e:
                                raise e
                    to_db = to_db.lstrip(',')
                    conn.execute(f"INSERT INTO {table_name}" + " values ({values})".format(values=(to_db)))

                    conn.commit()
            except Exception as e:
                conn.rollback()
                self.logger.exception(f'Exception raised while Inserting Data into Table: {e} ')

                shutil.move(f'{good_data_path}/{file}', bad_data_path)
                conn.close()
        conn.close()
        self.logger.info('End of Inserting Data into Table...')


    def export_csv(self, database_name, table_name):
        """
        Method to export database as CSV

        Args:
            database_name(string): The name of the db to be exported
            table_name(string): The name of table in the db
        Returns:
            None
        """
        self.file_from_db = f'{self.data_path}_validation/'
        self.file_name = 'InputFile.csv'
        try:
            self.logger.info('Start of export csv')
            conn = self.database_connection(database_name)
            sqlSelect = f"SELECT * FROM {table_name}"
            cursor = conn.cursor()
            cursor.execute(sqlSelect)
            results = cursor.fetchall()
            # Get the headers of the csv file
            headers = [i[0] for i in cursor.description]
            # Make the output directory for the CSV
            if not os.path.isdir(self.file_from_db):
                os.makedirs(self.file_from_db)
            # Open csv file and write to it
            csv_file = csv.writer(open(self.file_from_db + self.file_name, 'w', newline=''),delimiter=',', lineterminator='\r\n',quoting=csv.QUOTE_ALL, escapechar='\\')
            # Add header and data to csv
            csv_file.writerow(headers)
            csv_file.writerow(results)
            self.logger.info('End of writing to csv')
        except Exception as e:
            self.logger.exception(f'Exception raised while exporting data to csv: {e}')

