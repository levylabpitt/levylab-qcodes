# Imports
import sys
import json
import os
import time
import qcodes as qc
import zmq
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from levylabinst import LevyLabTestDB


sample_data_file_path = os.path.abspath('D:\\Code\\Github\\levylab-qcodes\\tests\\levylab_database\\sample_data.json')

# Send sample data to database
def upload_sample_data_to_db(sample_data, db):
    test_datetime = datetime.now()
    user_name = json.dumps(sample_data.get('user_name', ''))
    delivery_date = json.dumps(sample_data.get('delivery_date', ''))
    sample_id = json.dumps(sample_data.get('sample_id', ''))
    material = json.dumps(sample_data.get('material', ''))
    layout_file = json.dumps(sample_data.get('layout_file', ''))
    lead_id = json.dumps(sample_data.get('lead_id', ''))
    wirebonding = json.dumps(sample_data.get('wirebonding', ''))

    # Debugging print statements to see the data before inserting
    print("User Name:", user_name)
    print("Delivery Date:", delivery_date)
    print("Sample ID:", sample_id)
    print("Material:", material)  
    print("Layout File:", layout_file) 
    print("Lead ID:", lead_id) 
    print("Wirebonding Info:", wirebonding)                                               
    
    # Example insert query
    sql_insert_string = """
        INSERT INTO flexconfig_test (datetime, user_name, delivery_date, sample_id, material, layout_file, lead_id, wirebonding)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    db.cursor.execute(sql_insert_string, (test_datetime, user_name, delivery_date, sample_id, material, layout_file, lead_id, wirebonding))
    db.conn.commit()
    print("Data inserted successfully!")

# Retrieve the latest config from database
#def get_latest_config():
#    db = LocalDB(user="postgres")
    
#    sql_select_latest = """
#        SELECT user_name, delivery_date, sample_id, material, layout_file, lead_id, wirebonding
#        FROM sample_data
#        ORDER BY datetime DESC
#        LIMIT 1
#    """
#    result = db.execute_fetch(sql_select_latest, method='one')
#    db.close_connection()
    
#    if result:
#        print("Fetched Data from DB:", result)
#        return {
#            'wirebonding_info': result[0],
#            'kh_config_info': result[1],
#            'experiment_note_info': result[2],
#            'lockin_config_info': result[3]
#        }
#    else:
#        raise ValueError("No configuration data found in the database!")
    
# Function to push data to the database
def push_sample_data_to_db():
    if not os.path.exists(sample_data_file_path):
        raise FileNotFoundError(f"{sample_data_file_path} not found. Please provide the correct path.")
    
    # Open the config file and load the data
    try:
        with open(sample_data_file_path, 'r') as file:
            sample_data_data = json.load(file)

        # Create the database object
        levylab_test_db = LevyLabTestDB(user="levylab_test")
        
        # Upload the sample_data to the database
        upload_sample_data_to_db(sample_data_data, levylab_test_db)

        # Close the database connection
        levylab_test_db.close_connection()

    except Exception as e:
        print(f"Error reading or uploading config file: {e}")

def main():
    push_sample_data_to_db()
    
if __name__ == "__main__":
    main()

