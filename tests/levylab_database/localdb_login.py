"""
Login Handler for the Local database (hosted on CARINA)
PubuduW
"""

import os
import psycopg2

class LocalDB_Login:
    def __init__(self, username):
        self.username = username
        credentials = {
                            'hostname': 'localhost',
                            'port': 5433,
                            'database': 'postgres',
                            'user': username,
                            'password': 'flex'
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
            print("Connection to the local database established successfully")
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
    db = LocalDB_Login('postgres')
    # Perform database operations
    db.close()