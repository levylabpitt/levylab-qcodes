#%% Imports
import sys
import json
import qcodes as qc
import os
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#%% Create the instrument objects
from levylabinst import MCLockin
lockin_address = 'tcp://localhost:29170'
lockin = MCLockin('lockin', lockin_address, config=None)

# %%
lockin._set_sweepconfig(2,0.02,0.04,21)
lockin.Drain_Amp(0.3)
# %%
