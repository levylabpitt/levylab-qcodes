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

#-------------------------------------------------------------------------------------------
#%% Create the instrument objects
from levylabinst import MCLockin
lockin_address = 'tcp://localhost:29170'
lockin = MCLockin('lockin', lockin_address, config={'source': 1, 'drain': 2})

# ppms.field([1,5])
# print(ppms._send_command('Get Magnet'))
# ---------------------------------------------------------------------

# %% Station
station = qc.Station()
station.add_component(lockin)


# %% Experiment
#test_exp = load_or_create_experiment('test_exp_1', sample_name='SimWaveguide_1')

#%%Measurement after sweeping
import time
lockin._set_sweepconfig(1,0.04,0.09,"Ramp /",5,9)
lockin._set_state('start sweep')
time.sleep(12) #To make sure, the sweeping is done completely. The sleep time is more than sweeping time.
dataset=lockin._get_sweep_data() 

#%%Plotting dataset
plot_dataset(dataset,captured_run_id=1)

#%%










