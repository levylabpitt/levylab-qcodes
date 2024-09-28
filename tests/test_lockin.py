#%% Imports
import sys
import json
import time
import qcodes as qc
import os
import numpy as np
import zmq
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#%% Create the instrument objects
from levylabinst import MCLockin
lockin_address = 'tcp://localhost:29170'
config_file_path = os.path.abspath('D:\\Code\\Github\\levylab-qcodes\\tests\\experiment.config.json')
lockin = MCLockin('lockin', lockin_address, config_file = config_file_path)

# %%
lockin.dashboard()

# %%
lockin.reload_config()

# %%
lockin.gate_Freq(13)

# %%
lockin.reset_parameters()

# %%
lockin.reset_all_parameters()
# %%
