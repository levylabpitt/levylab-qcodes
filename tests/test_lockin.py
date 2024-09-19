#%% Imports
import sys
import json
import qcodes as qc
import os
import numpy as np
import time
import matplotlib.pyplot as plt
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#%% Create the instrument objects
from levylabinst import MCLockin
lockin_address = 'tcp://localhost:29170'
lockin = MCLockin('lockin', lockin_address, config=None)

# %%
lockin._set_sweepconfig(2,0.04,0.09,"Ramp /",4,10)
lockin._set_state('start sweep')
Xresults = [] #To store the values of Xresults while sweeping

#running the while loop for the given sweeptime and storing the X-values in the Xresults
t_end = time.time() + 10 #sweeptime = 5s
while time.time() < t_end: 
    d = lockin.source_X()
    Xresults.append(d)

#determining the length for Xresults and made an array
l = len(Xresults) 
Xlist = np.linspace(1,l,l)
         
Xarray = np.array(Xlist) 

#Plotting the Xresults 
plt.plot(Xarray, Xresults, marker='o')
plt.xlabel('points')
plt.ylabel('Sweep Results X(V)')
plt.show()


#lockin.Drain_Amp(0.3)
# %%
