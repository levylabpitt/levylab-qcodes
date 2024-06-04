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

# ---------------------------------------------------------------------
#%% Create the instrument objects
from levylabinst import PPMSSim, MCLockin
ppms_address = 'tcp://localhost:29270'
lockin_address = 'tcp://localhost:29170'
ppms = PPMSSim('ppms', ppms_address)
lockin = MCLockin('lockin', lockin_address)
# ppms.field([1,5])
# print(ppms._send_command('Get Magnet'))
# ---------------------------------------------------------------------
# %% Station
station = qc.Station()
station.add_component(ppms)
station.add_component(lockin)
# ---------------------------------------------------------------------
# %% Database
initialise_or_create_database_at(r'D:\qcodesdb\experiment.db')
qc.config.core.db_location
# ---------------------------------------------------------------------
# %% Experiment
test_exp = load_or_create_experiment('test_exp', sample_name='SimWaveguide')
# ---------------------------------------------------------------------
# %% doNd Measurement
sweep = LinSweep(lockin.gate, 0, 0.1, 500, 0.01)
dond(sweep, lockin.drain, measurement_name='doNd_measurement', exp=test_exp, show_progress=True)

# %% Explore Experiments and Datasets
experiments()
test_exp.data_sets()
# ---------------------------------------------------------------------
# %% Load and Plot Dataset
dataset = load_by_run_spec(experiment_name='test_exp', captured_run_id=1)
plot_dataset(dataset)
# ---------------------------------------------------------------------
# %% Interactive Widget
experiments_widget(sort_by='run_id')
# %%