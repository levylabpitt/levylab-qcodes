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

# ---------------------------------------------------------------------
#%% Create the instrument objects
from levylabinst import PPMSSim, MCLockin
ppms_address = 'tcp://localhost:29270'
lockin_address = 'tcp://localhost:29170'
ppms = PPMSSim('ppms', ppms_address)
lockin = MCLockin('lockin', lockin_address, config={'source': 1, 'drain': 1, 'gate': 2})
# ppms.field([1,5])
# print(ppms._send_command('Get Magnet'))
# ---------------------------------------------------------------------
# %% Station
station = qc.Station()
station.add_component(ppms)
station.add_component(lockin)
# ---------------------------------------------------------------------
# %% Database
db_file_path = r'C:\qcodesdb\experiment.db'
initialise_or_create_database_at(db_file_path)
qc.config.core.db_location
# ---------------------------------------------------------------------
# %% Experiment
test_exp = load_or_create_experiment('test_exp', sample_name='SimWaveguide')
# ---------------------------------------------------------------------

# %% do1d Measurement
import IPython.lib.backgroundjobs as bg
from plottr.apps import inspectr

jobs = bg.BackgroundJobManager()
jobs.new(inspectr.main, db_file_path)

# %% do1d Measurement
do1d(lockin.gate_DC, 0, 0.1, 500, 0.01, lockin.drain_X, measurement_name='do1d_measurement', exp=test_exp, write_period=0.1, show_progress=True, do_plot=True)

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
