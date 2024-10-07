#%% Imports
import sys
import json
import qcodes as qc
import os
import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#%% Create the instrument objects
from levylabinst import MCLockin
lockin_address = 'tcp://localhost:29170'
lockin = MCLockin('lockin', lockin_address, config={"gate1":1, "gate2":2, "gate3":3})

# %% Psuedo code for sweep checking

'''
1. check for the lockin status (if idle, then start/if sweeping, abort the request)
2. set config
3. start the sweep
3*. function to do real-time plotting (real_time_plotting)
4. wait for the duration of the sweep (initial wait + sweep time)
5. query the lock-in status to check whether the sweep is stopped
6. return the results

def real_time_plotting(self, refresh time):
    query for the data with a given refresh time and plot the results as the sweep is going on.
'''

#%% State checking

#Check lock-in status
lockin.state()

#%% Sweep configuration
lockin._set_1dsweepconfig([[1,0.04,0.10,"Ramp /"],[2,0.05,0.11,"Ramp /"],[3,0.06,0.12,"Smooth Ramp _/"]],5,6)

#%%sweeping
lockin._sweep_process()

#%% Getting AI Data
lockin._plot_SweepAI()

#%% Getting AO data
lockin._plot_SweepAO()

#%% Getting Sweep X data
lockin._plot_SweepX()

#%% Getting Sweep Y data
lockin._plot_SweepY()

#%% Real-time plottting
'''print(X)
print(Y)
'''
#%%Real-time plotting
'''npt = len(X)

tpoints = np.linspace(1, len(X), len(X))
tarray = np.array(tpoints)

print(tarray)

plt.plot(tarray, X, label = 'X', marker = 'o')
plt.plot(tarray, Y, label = 'Y', marker = 'o')
plt.title('real-time plotting during sweeping')
plt.xlabel('points')
plt.ylabel('X(V) and Y(V)')
plt.legend()
plt.show()
plt.savefig("real-time plotting.png")
'''
