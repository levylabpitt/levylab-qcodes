#%% Imports
import sys
import json
import os
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#%% Create the instrument objects
from levylabinst import *
lockin_address = 'tcp://localhost:29170'
ppms_address = 'tcp://localhost:29270'
config_waveguide = {'source': 1, 'drain': 1, 'gate': 2}
lockin = MCLockin('lockin', lockin_address, config=config_waveguide)
ppms = PPMSSim('ppms', ppms_address)

for temp in np.linspace(200, 210, 5):
    ppms.temperature.set([temp,10])
    x,y = lockin.sweep1d(2, 0, 0.1, 10, 1)
    temp = ppms.temperature()

