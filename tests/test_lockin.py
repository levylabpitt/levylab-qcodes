#%% Imports
import sys
import json
import time
import qcodes as qc
import os
import numpy as np
import zmq
from datetime import datetime
from config_watcher import get_latest_config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from levylabinst import MCLockin
from levylabinst.dashboard import Dashboard
lockin_address = 'tcp://localhost:29170'
# %% Database handling
latest_config_data = get_latest_config()

# Use the latest config data
lockin_config = latest_config_data.get('lockin_config_info', {})
kh_config_info = latest_config_data.get('kh_config_info', [])
wirebonding_info = latest_config_data.get('wirebonding_info', 'No info available')
experiment_note_info = latest_config_data.get('experiment_note_info', 'No info available')

if 'lockin' in qc.Instrument._all_instruments:
    lockin = qc.Instrument._all_instruments['lockin']
    lockin.close()

lockin = MCLockin('lockin', lockin_address, config={'lockin_config_info': lockin_config})


# %%
dashboard = Dashboard(lockin_config_info=lockin_config, 
    kh_config_info=kh_config_info, 
    wirebonding_info=wirebonding_info, 
    experiment_note_info=experiment_note_info)
dashboard.launch()

# %%
print("Latest config data being passed:", latest_config_data)

# %%
lockin.source_Amp(6)
# %%
lockin.reset_all_parameters()
