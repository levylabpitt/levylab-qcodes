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
from levylabinst import MCLockin, LocalDB
lockin_address = 'tcp://localhost:29170'

# %% Database handling (PubuduW)
db = LocalDB(user="postgres")

# Fetch the latest config from the database
def get_latest_config_from_db(db):
    # Query to get the most recent config entry
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
    
latest_config_data = get_latest_config_from_db(db)

#%% Fetch the latest config from the database

# Use the latest config data
lockin_config = latest_config_data['lockin_config_info']
wirebonding_info = latest_config_data.get('wirebonding_info', 'No info available')
krohn_hite_info = latest_config_data.get('krohn_hite_info', 'No info available')
experiment_note_info = latest_config_data.get('experiment_note_info', 'No info available')

lockin_config = {
    'lockin_config_info': lockin_config
}

if 'lockin' in qc.Instrument._all_instruments:
    lockin = qc.Instrument._all_instruments['lockin']
    lockin.close()

lockin = MCLockin('lockin', lockin_address, config=lockin_config)

# Display the latest config info or perform operations
print(f"Lockin Config: {lockin_config}")
print(f"Wirebonding Info: {wirebonding_info}")
print(f"Krohn-Hite Info: {krohn_hite_info}")
print(f"Experiment Notes: {experiment_note_info}")

# %%
lockin.dashboard(wirebonding_info, krohn_hite_info, experiment_note_info)

# %%
print("Latest config data being passed:", latest_config_data)

# %%
lockin.source_Amp(6)

# %%
lockin.reset_parameters()

# %%
lockin.reset_all_parameters()

# %%
lockin.reload_config(latest_config_data)