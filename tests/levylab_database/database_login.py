"""
Login Handler for the Levylab database
"""

import os
import psycopg2

class LevylabDB_Login:
    def __init__(self, username, config_path=None):
        self.username = username
        self.config_path = config_path or os.path.join(os.getenv('APPDATA'), 'postgresql', 'pgpass.conf')
        self.credentials = self.get_credentials()
        # self.connection = self.connect()

    def get_credentials(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found at {self.config_path}")

        with open(self.config_path, 'r') as file:
            for line in file:
                if line.strip() and not line.startswith('#'):
                    hostname, port, database, user, password = line.strip().split(':')
                    if user == self.username:
                        return {
                            'hostname': hostname,
                            'port': port,
                            'database': database,
                            'user': user,
                            'password': password
                        }
        raise ValueError(f"Credentials for username '{self.username}' not found")

    def connect(self):
        try:
            connection = psycopg2.connect(
                host=self.credentials['hostname'],
                port=self.credentials['port'],
                database=self.credentials['database'],
                user=self.credentials['user'],
                password=self.credentials['password']
            )
            print("Connection to database established successfully")
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
    db = LevylabDB_Login('llab_admin')
    # Perform database operations
    db.close()