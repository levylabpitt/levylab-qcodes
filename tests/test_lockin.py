#%% Imports
import sys
import json
import qcodes as qc
import os
import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#%% Create the instrument objects
from levylabinst import MCLockin
lockin_address = 'tcp://localhost:29170'
lockin = MCLockin('lockin', lockin_address, config={"gate1":1})

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


#%% Sweep configuration for multiple sweep
sweep_config = [[1,0.08,0.15,"Ramp /"],
                [2,0.04,0.10,"Smooth Ramp _/"],
                [3,0.09,0.17,"Table",[1,3,5,7]],
                [4,0.05,0.20,"Smooth Ramp _/"]]


#%% Mutliple sweep
lockin.multisweep(sweep_config,5,6,None)


#%% 2dsweep
X1 = [] #for storing the sweep results

B = [1,1.5,2,2.5] #Magnetic field

for values in B: 
       x = lockin.sweep(2,0,0.1,"Ramp /",5,6,1) 
       X1.append(x[2]) 
        

#%%Print X1
print(X1)

#%% 3d plotting
fig = plt.figure()
ax = fig.add_subplot(111, projection= '3d')

n = len(X1[0])
xlist = np.linspace(0,n-1,n)
xarray = np.array(xlist)

x1 = xarray
y1 = X1[0]
z1 = np.full(n,B[0])

x2 = xarray
y2 = X1[1]
z2 = np.full(n,B[1])

x3 = xarray
y3 = X1[2]
z3 = np.full(n,B[2])

x4 = xarray
y4 = X1[3]
z4 = np.full(n,B[3])

ax.scatter(x1, y1, z1, c='k', marker = '*')
ax.scatter(x2, y2, z2, c='r', marker = '*')
ax.scatter(x3, y3, z3, c='b', marker = '*')
ax.scatter(x4, y4, z4, c='g', marker = '*')

ax.set_xlabel('Samples')
ax.set_ylabel('AI1')
ax.set_zlabel('Magnetic field')

plt.show()

#%% Intensity plotting



# %%
