"""
Script to connect to and manage the local pgsql database
PubuduW
"""
from .levylab_test_db_login import LevyLabTestDB_Login

class LevyLabTestDB(LevyLabTestDB_Login):
    def __init__(self, user):
        super().__init__(user)
        pgpassconf_path = ''
        self.conn = self.connect()
        self.cursor = self.conn.cursor()

    def close_connection(self):
        self.conn.close()
        self.cursor.close()

    def execute_fetch(self, sql_string, method='one', size=5):
        self.cursor.execute(sql_string)
        if method == 'one':
            return self.cursor.fetchone()
        elif method == 'many':
            return self.cursor.fetchmany(size=size)
        elif method == 'all':
            return self.cursor.fetchall()
    
if __name__ == "__main__":
    levylab_test_db = LevyLabTestDB("levylab_test")
    # Example query
    # TODO: Should have a string handler for instrument parameters
    sql_string = """SELECT datetime, data FROM flexconfig_test
                """
    print(levylab_test_db.execute_fetch(sql_string, method='many', size=5))
    levylab_test_db.close_connection()