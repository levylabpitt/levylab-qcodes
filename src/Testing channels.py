#%% Imports
import sys
import json
import qcodes as qc
import os
import numpy as np
import qcodes as qc
## Logging
from qcodes.logger import start_all_logging
## Multidimensional scanning module
from qcodes.dataset import (
    LinSweep,
    Measurement,
    do1d,
    dond,
    experiments,
    initialise_or_create_database_at,
    load_by_run_spec,
    load_or_create_experiment,
    plot_dataset,
)
## Using interactive widget
from qcodes.interactive_widget import experiments_widget

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
start_all_logging()

#------------------------------------------------------------------------------
#%% Create the instrument objects
from levylabinst import PPMSSim, MCLockin
ppms_address = 'tcp://localhost:29270'
lockin_address = 'tcp://localhost:29170'
ppms = PPMSSim('ppms', ppms_address)
lockin = MCLockin('lockin', lockin_address)
# ppms.field([1,5])
# print(ppms._send_command('Get Magnet'))
#---------------------------------------------------------------------------
##Controlling the channels 
#lockin._gate_getter()
# lockin._gate_setter(6)
lockin.frequency(20)
# lockin.frequency2(0)
# lockin.frequency5(20)
# lockin.amplitude7(0)
# lockin.amplitude5(0.08)
# lockin.DC7(0)
# lockin.DC2(0)
# lockin.DC5(0.06)
# lockin.phase5(30)

# %%
