# Imports
import sys
import json
import os
import time
import qcodes as qc
import zmq
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from levylabinst import MCLockin, LocalDB

# Send data to database
def upload_config_to_db(config_data, db):
    test_datetime = datetime.now()
    wirebonding_info = json.dumps(config_data.get('wirebonding_info', {}))
    krohn_hite_info = json.dumps(config_data.get('krohn_hite_info', {}))
    experiment_note_info = json.dumps(config_data.get('experiment_note_info', {}))
    lockin_config_info = json.dumps(config_data.get('lockin_config_info', {}))                                                         
    
    # Example insert query
    sql_insert_string = """
        INSERT INTO flexconfig_test (datetime, wirebonding_info, krohn_hite_info, experiment_info, lockin_config_info)
        VALUES (%s, %s, %s, %s, %s)
    """
    db.cursor.execute(sql_insert_string, (test_datetime, wirebonding_info, krohn_hite_info, experiment_note_info, lockin_config_info))
    db.conn.commit()
    print("Data inserted successfully!")

# Retrieve the latest config from database
def get_latest_config():
    db = LocalDB(user="postgres")
    
    sql_select_latest = """
        SELECT wirebonding_info, krohn_hite_info, experiment_info, lockin_config_info
        FROM flexconfig_test
        ORDER BY datetime DESC
        LIMIT 1
    """
    result = db.execute_fetch(sql_select_latest, method='one')
    db.close_connection()
    
    if result:
        return {
            'wirebonding_info': result[0],
            'krohn_hite_info': result[1],
            'experiment_note_info': result[2],
            'lockin_config_info': result[3]
        }
    else:
        raise ValueError("No configuration data found in the database!")

# Watchdog Event Handler
class ConfigFileHandler(FileSystemEventHandler):
    def __init__(self, config_file_path, db):
        self.config_file_path = config_file_path
        self.db = db

    def on_modified(self, event):
        if event.src_path == self.config_file_path:
            print(f"Detected change in {self.config_file_path}. Reloading and uploading data to database...")
            try:
                with open(self.config_file_path, 'r') as file:
                    config_data = json.load(file)
                upload_config_to_db(config_data, self.db)
            except Exception as e:
                print(f"Error reading or uploading config file: {e}")

# Main code to set up and start watching the file
def main():
    config_file_path = os.path.abspath('D:\\Code\\Github\\levylab-qcodes\\tests\\expconfig.json')
    if not os.path.exists(config_file_path):
        raise FileNotFoundError(f"{config_file_path} not found. Please provide the correct path.")

    # Create the database object
    db = LocalDB(user="postgres")
    
    # Create event handler and observer
    event_handler = ConfigFileHandler(config_file_path, db)
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(config_file_path), recursive=False)
    
    # Start the observer
    observer.start()
    print(f"Started watching {config_file_path} for changes.")
    
    try:
        while observer.is_alive():
            time.sleep(1)  # Keep the script running to monitor changes
    finally:
        observer.stop()
        observer.join()
        print("Observer stopped gracefully.")

    # Close the database connection
    db.close_connection()

if __name__ == "__main__":
    main()
