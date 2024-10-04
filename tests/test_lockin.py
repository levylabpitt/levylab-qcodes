#%% Imports
import sys
import json
import time
import qcodes as qc
import os
import numpy as np
import zmq
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#%% Create the instrument objects
from levylabinst import MCLockin, LocalDB
lockin_address = 'tcp://localhost:29170'

# %% Database handling (PubuduW)
db = LocalDB(user="postgres")

# Fetch the latest config from the database
def get_latest_config_from_db(db):
    # Query to get the most recent config entry
    sql_select_latest = """
        SELECT data FROM flexconfig_test
        ORDER BY datetime DESC
        LIMIT 1
    """
    result = db.execute_fetch(sql_select_latest, method='one')
    
    if result:
        latest_config = result[0]  # Extract the data from the tuple
        if isinstance(latest_config, str):  # If it's a string, parse it
            return json.loads(latest_config)
        elif isinstance(latest_config, dict):  # If it's already a dict, return it directly
            return latest_config
        else:
            raise TypeError("Unexpected data format in the database.")
    else:
        raise ValueError("No configuration data found in the database!")

# Fetch the latest config from the database
latest_config_data = get_latest_config_from_db(db)

# Use the latest config data
lockin_config = latest_config_data['lockin_config_info']
wirebonding_info = latest_config_data.get('wirebonding_info', 'No info available')
krohn_hite_info = latest_config_data.get('krohn_hite_info', 'No info available')
experiment_note_info = latest_config_data.get('experiment_note_info', 'No info available')

lockin_config = {
    'lockin_config_info': lockin_config
}
lockin = MCLockin('lockin', lockin_address, config=lockin_config)

test_datetime = datetime.now()
json_data = json.dumps(latest_config_data)

# Example insert query (this was chatGPT generated)
sql_insert_string = """
    INSERT INTO flexconfig_test (datetime, data)
    VALUES (%s, %s)
"""
db.cursor.execute(sql_insert_string, (test_datetime,json_data))
db.conn.commit()
print("Data inserted successfully!")

time.sleep(0.5) # delay to update the database (this is not needed)

# Example select query
sql_select_string = """SELECT datetime, data FROM flexconfig_test
                    """
print(*db.execute_fetch(sql_select_string, method='many', size=10), sep="\n")

# close db
db.close_connection()

# %%
lockin.dashboard(wirebonding_info, krohn_hite_info, experiment_note_info)

# %%
print("Latest config data being passed:", latest_config_data)
lockin.reload_config(latest_config_data)

# %%
lockin.source_Amp(6)

# %%
lockin.reset_parameters()

# %%
lockin.reset_all_parameters()
# %%
