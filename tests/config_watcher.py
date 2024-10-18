# Imports
import sys
import json
import os
import time
import qcodes as qc
import zmq
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from levylabinst import LocalDB

config_file_path = os.path.abspath('D:\\Code\\Github\\levylab-qcodes\\tests\\expconfig.json')

# Send data to database
def upload_config_to_db(config_data, db):
    test_datetime = datetime.now()
    wirebonding_info = json.dumps(config_data.get('wirebonding_info', {}))
    kh_config_info = json.dumps(config_data.get('kh_config_info', {}))
    experiment_note_info = json.dumps(config_data.get('experiment_note_info', {}))
    lockin_config_info = json.dumps(config_data.get('lockin_config_info', {}))

    # Debugging print statements to see the data before inserting
    print("Wirebonding Info:", wirebonding_info)
    print("KH Config Info:", kh_config_info)
    print("Experiment Note Info:", experiment_note_info)
    print("Lockin Config Info:", lockin_config_info)                                                
    
    # Example insert query
    sql_insert_string = """
        INSERT INTO flexconfig_test (datetime, wirebonding_info, kh_config_info, experiment_info, lockin_config_info)
        VALUES (%s, %s, %s, %s, %s)
    """
    db.cursor.execute(sql_insert_string, (test_datetime, wirebonding_info, kh_config_info, experiment_note_info, lockin_config_info))
    db.conn.commit()
    print("Data inserted successfully!")

# Retrieve the latest config from database
def get_latest_config():
    db = LocalDB(user="postgres")
    
    sql_select_latest = """
        SELECT wirebonding_info, kh_config_info, experiment_info, lockin_config_info
        FROM flexconfig_test
        ORDER BY datetime DESC
        LIMIT 1
    """
    result = db.execute_fetch(sql_select_latest, method='one')
    db.close_connection()
    
    if result:
        print("Fetched Data from DB:", result)
        return {
            'wirebonding_info': result[0],
            'kh_config_info': result[1],
            'experiment_note_info': result[2],
            'lockin_config_info': result[3]
        }
    else:
        raise ValueError("No configuration data found in the database!")
    
# Function to push data to the database
def push_config_to_db():
    if not os.path.exists(config_file_path):
        raise FileNotFoundError(f"{config_file_path} not found. Please provide the correct path.")
    
    # Open the config file and load the data
    try:
        with open(config_file_path, 'r') as file:
            config_data = json.load(file)

        # Create the database object
        db = LocalDB(user="postgres")
        
        # Upload the config to the database
        upload_config_to_db(config_data, db)

        # Close the database connection
        db.close_connection()

    except Exception as e:
        print(f"Error reading or uploading config file: {e}")

def main():
    push_config_to_db()
    
if __name__ == "__main__":
    main()

