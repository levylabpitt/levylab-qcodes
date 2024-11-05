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

#%% Sweep configuration
sweep_config = [[1,0.08,0.15,"Ramp /"],
                [2,0.04,0.10,"Smooth Ramp _/"],
                [3,0.09,0.17,"Table",[1,3,5,7]],
                [4,0.05,0.20,"Smooth Ramp _/"]]

lockin._set_1dsweepconfig(sweep_config,5,6)

#%%sweeping
lockin._sweep_process()


#%% Defining the plotting functions
def _plot_SweepAI(self) -> None: 
        data = lockin._get_sweep_data()
        ai_array = [entry['Y'] for entry in data['result']['AI_wfm']]
        dfai = pd.DataFrame(ai_array).transpose()
        print(dfai)
        #dfai.to_csv('/Users/SoumyaR/Documents/Data/Sweep AI data.csv')
        plt.plot(dfai)
        plt.title('Sweep AI')
        plt.xlabel('Samples')
        plt.ylabel('Sweep AI (V)')
        plt.show()
        #plt.savefig("Sweep AI.png", dpi=500)


def _plot_SweepAO(self) -> None:
        data = lockin._get_sweep_data()
        ao_array = [entry['Y'] for entry in data['result']['AO_wfm']]
        dfao = pd.DataFrame(ao_array).transpose()
        print(dfao)
        #dfao.to_csv('/Users/SoumyaR/Documents/Data/Sweep AO data.csv')
        plt.plot(dfao)
        plt.title('Sweep AO')
        plt.xlabel('Samples')
        plt.ylabel('Sweep AO (V)')
        plt.show()
        #plt.savefig("Sweep AO.png", dpi=500)

def _plot_SweepY(self) -> None:
        data = lockin._get_sweep_data()
        y_array = [entry['Y'] for entry in data['result']['Y_wfm']]
        dfy = pd.DataFrame(y_array).transpose()
        print(dfy)
        #dfy.to_csv('/Users/SoumyaR/Documents/Data/Sweep Y data.csv')
        plt.plot(dfy)
        plt.title('Sweep Y')
        plt.xlabel('Samples')
        plt.ylabel('Sweep Y results (V)')
        plt.show()
        #plt.savefig("Sweep Y.png", dpi=500)

def _plot_SweepX(self) -> None:
        data = lockin._get_sweep_data()
        x_array = [entry['Y'] for entry in data['result']['X_wfm']]
        dfx = pd.DataFrame(x_array).transpose()
        print(dfx)
        #dfx.to_csv('/Users/SoumyaR/Documents/Data/Sweep X data.csv')
        plt.plot(dfx)
        plt.title('Sweep X')
        plt.xlabel('Samples')
        plt.ylabel('Sweep X results (V)')
        plt.show()
        #plt.savefig("Sweep X.png", dpi=500) 

#%% Getting AI Data
lockin._plot_SweepAI()

#%% Getting AO data
lockin._plot_SweepAO()

#%% Getting Sweep X data
lockin._plot_SweepX()

#%% Getting Sweep Y data
lockin._plot_SweepY()

#%%2d sweep configurations
B = [1,1.5,2,2.5] #Magnetic field

#sweep configurations
sweep_config = [[2,0,0.1,"Ramp /"]]


#%% 2dsweep & getting channel 1 of sweep X results
X1 = lockin._sweep_2d_X1(B,sweep_config,5,6)

#print(X1)

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



