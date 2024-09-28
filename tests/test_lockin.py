#%% Imports
import sys
import json
import qcodes as qc
import os
import numpy as np
from qcodes.dataset import (
    LinSweep,
    Measurement,
    dond,
    experiments,
    initialise_or_create_database_at,
    load_by_run_spec,
    load_or_create_experiment,
    plot_dataset,
    plot_by_id
)
from qcodes.interactive_widget import experiments_widget

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#%% Create the instrument objects
from levylabinst import *
lockin_address = 'tcp://localhost:29170'
config_waveguide = {'source': 1, 'drain': 1, 'gate': 2}
lockin = MCLockin('lockin', lockin_address, config=config_waveguide)

# %%
station = qc.Station()
station.add_component(lockin)

# %%
initialise_or_create_database_at(r'C:\qcodesdb\experiment.db')
qc.config.core.db_location

# %% Experiment
sweep_exp = load_or_create_experiment('sweep_exp_test', sample_name='SimWaveguide')

# %% Measurement
meas = Measurement()
meas.register_parameter(lockin.gate_DC)
meas.register_parameter(lockin.drain_X, setpoints=(lockin.gate_DC,))

with meas.run() as datasaver:
    x,y = lockin.sweep1d(2, 0, 0.1, 10, 1)
    datasaver.add_result((lockin.drain_X, y),
                         (lockin.gate_DC, x))

# %%
ax, cbax = plot_by_id(datasaver.run_id)
experiments_widget()
# %%
