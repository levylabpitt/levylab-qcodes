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
lockin._set_sweepconfig(1,0.05,0.10,"Ramp /",5,40)
lockin.state('start sweep')


#lockin.Drain_Amp(0.3)
# %%
