"""
Login Handler for the Local database (hosted on CARINA)
PubuduW
"""

import os
import psycopg2

class LevyLabTestDB_Login:
    def __init__(self, llab_writer):
        self.username = llab_writer
        credentials = {
                            'hostname': '10.226.177.162',
                            'port': 5432,
                            'database': 'levylab_test',
                            'user': llab_writer,
                            'password': '2ll0ab22writer@!'
        # TODO: Password should come from a config file. Should not be hardcoded.
        
                        }
        self.credentials = credentials
        # self.connection = self.connect()

    def connect(self):
        try:
            connection = psycopg2.connect(
                host=self.credentials['hostname'],
                port=self.credentials['port'],
                database=self.credentials['database'],
                user=self.credentials['user'],
                password=self.credentials['password']
            )
            print("Connection to the levylab_test database established successfully")
            return connection
        except Exception as e:
            print(f"Failed to connect to database: {e}")
            raise

    def close(self):
        if self.connection:
            self.connection.close()
            print("Connection to database closed")

# Example usage
if __name__ == '__main__':
    levylab_test_db = LevyLabTestDB_Login('levylab_test')
    # Perform database operations
    levylab_test_db.close()