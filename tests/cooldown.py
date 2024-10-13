#%% Imports
import sys
import qcodes as qc
import os
import numpy as np
import matplotlib
from qcodes.interactive_widget import experiments_widget
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

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from levylabinst import *

#%% Create the instrument objects
lockin_address = 'tcp://localhost:29170'
ppms_address = 'tcp://localhost:29270'
config_waveguide = {'source': 1, 'drain': 1, 'gate': 2}

lockin = MCLockin('lockin', lockin_address, config=config_waveguide)
ppms = PPMSSim('ppms', ppms_address)

#%% Define new parameters
lockin.add_parameter('cond2T', unit='sigma', label='2T Conductance')

# %% Create the database and initialize plottr
db_file_path = r'C:\qcodesdb\experiment.db'
initialise_or_create_database_at(db_file_path)
qc.config.core.db_location
import IPython.lib.backgroundjobs as bg
from plottr.apps import inspectr
jobs = bg.BackgroundJobManager()
jobs.new(inspectr.main, db_file_path)

# %% Create the station, experiment and measurement
station = qc.Station(lockin, ppms)
sweep_exp = load_or_create_experiment('cooldown', sample_name='SimWaveguide')
meas = Measurement(name='cooldown GvT', exp=sweep_exp)

meas.register_parameter(ppms.temperature)
meas.register_parameter(lockin.cond2T , setpoints=(ppms.temperature,))

ppms.settemp_async([10, 100])

with meas.run() as datasaver:
    while ppms.temperature() > 10:
        c2T = lockin.drain_X()/0.1
        temp = ppms.temperature()
        datasaver.add_result((lockin.cond2T, c2T),
                            (ppms.temperature, temp))

# %%
ax, cbax = plot_by_id(datasaver.run_id)
experiments_widget()
# %%
