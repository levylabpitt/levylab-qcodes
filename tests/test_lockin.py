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
config_file_path = os.path.abspath('D:\\Code\\Github\\levylab-qcodes\\tests\\expconfig.json')
if not os.path.exists(config_file_path):
    raise FileNotFoundError(f"{config_file_path} not found. Please provide the correct path.")
with open(config_file_path, 'r') as file:
    config_data = json.load(file)
lockin_config = config_data['lockin_config_info']
wirebonding_info = config_data.get('wirebonding_info', 'No info available')
krohn_hite_info = config_data.get('krohn_hite_info', 'No info available')
experiment_note_info = config_data.get('experiment_note_info', 'No info available')
lockin = MCLockin('lockin', lockin_address, config_file = config_file_path)

# %% Database handling (PubuduW)
db = LocalDB(user="postgres")

test_datetime = datetime.now()
json_data = json.dumps(config_data)

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
lockin.reload_config()

# %%
lockin.source_Amp(6)

# %%
lockin.reset_parameters()

# %%
lockin.reset_all_parameters()
# %%
