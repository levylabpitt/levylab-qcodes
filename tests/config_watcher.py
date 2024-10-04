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

# Database handler function
def upload_config_to_db(config_data, db):
    test_datetime = datetime.now()
    json_data = json.dumps(config_data)
    
    # Example insert query
    sql_insert_string = """
        INSERT INTO flexconfig_test (datetime, data)
        VALUES (%s, %s)
    """
    db.cursor.execute(sql_insert_string, (test_datetime, json_data))
    db.conn.commit()
    print("Data inserted successfully!")

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
