"""
Script to connect to and manage the levylab pgsql database
"""
from database_login import LevylabDB_Login

class LevyLabDB(LevylabDB_Login):
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
    db = LevyLabDB("llab_admin")
    # Example query
    # TODO: Should have a string handler for instrument parameters
    sql_string = """SELECT time, d017 FROM llab_011
                    WHERE d017 IS NOT NULL
                    AND time BETWEEN '2024-06-04 21:00:08.638105' AND '2024-06-04 22:04:23.543921'"""
    print(db.execute_fetch(sql_string, method='many', size=5))
    db.close_connection()