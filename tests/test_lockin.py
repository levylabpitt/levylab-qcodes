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
ppms_address = 'tcp://localhost:29270'
config_waveguide = {'source': 1, 'drain': 1, 'gate': 2}
lockin = MCLockin('lockin', lockin_address, config=config_waveguide)
ppms = PPMSSim('ppms', ppms_address)

# %%
station = qc.Station()
station.add_component(lockin)
station.add_component(ppms)

# %%
db_file_path = r'C:\qcodesdb\experiment.db'
initialise_or_create_database_at(db_file_path)
qc.config.core.db_location

# %% Experiment
# sweep_exp = load_or_create_experiment('sweep_exp_test', sample_name='SimWaveguide')

# import IPython.lib.backgroundjobs as bg
# from plottr.apps import inspectr

# jobs = bg.BackgroundJobManager()
# jobs.new(inspectr.main, db_file_path)


# %% Measurement
meas = Measurement()
meas.register_parameter(ppms.temperature)
meas.register_parameter(lockin.gate_DC)
meas.register_parameter(lockin.drain_X, setpoints=(lockin.gate_DC, ppms.temperature))

with meas.run() as datasaver:
    for temp in np.linspace(200, 210, 5):
        # *Temperature range should be exactly divisible by the number of points
        ppms.temperature.set([temp,10])
        x,y = lockin.sweep1d(2, 0, 0.1, 10, 1)
        temp = ppms.temperature()
        datasaver.add_result((lockin.drain_X, y),
                            (lockin.gate_DC, x),
                            (ppms.temperature, temp))

# %%
ax, cbax = plot_by_id(datasaver.run_id)
experiments_widget()
# %%
