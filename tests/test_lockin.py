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
lockin = MCLockin('lockin', lockin_address, config={"source":1})

#%% If condition approach
'''def start_sweep():
    lockin._set_state('start sweep')
    return True
'''
'''
lockin._set_sweepconfig(1,0.04,0.09,"Ramp /",6,10)
start_sweep()
sweep_completed = False
while not sweep_completed:
    sweep_completed = start_sweep()

    if sweep_completed:
        data = lockin._get_sweep_data()
    else:
        print("Sweep not completed, waiting...")
        time.sleep(1)

    '''

# %%Sweep started

#lockin.state('start sweep')


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

#%% Sweeping

#Check lock-in status
lockin.state()

#sweep configuration
lockin._set_sweepconfig(1,0.04,0.09,"Ramp /",4,5)

#start sweeping
lockin._set_state('start sweep')

#Wait for the sweep duration
time.sleep(9)

#To check whether Sweeping is completed or not

print(lockin.state())
while lockin.state() == 'sweeping':
    time.sleep(0.5)

# while status:
#    if status == 'sweeping':
#        print('still sweeping')
#        time.sleep(1)
#    else:
#       print("Sweep completed")
#       status = False

print('sweep completed')
print(lockin.state())  #verification   


#%% Acquiring data
data = lockin._get_sweep_data()

#sdata= pd.DataFrame(data)

# %%Saving data into .csv files
#sdata.to_csv('sweep dataset.csv', index=False)
#print(data) 

##data organizing

# %%Extract the "AI_wfm" array
ai_arrays = [entry['Y'] for entry in data['result']['AI_wfm']]

#%% Convert to DataFrame
dfai = pd.DataFrame(ai_arrays).transpose()

#%%Printing the data
print(dfai)

#%%Saving the data
AIdata = dfai.to_csv('Sweep AI data.csv')

# %%Extract the "AO_wfm" array
ao_array = [entry['Y'] for entry in data['result']['AO_wfm']]

# %%Convert to DataFrame
dfao = pd.DataFrame(ao_array).transpose()

#%%Printing the data
print(dfao)

#%%Saving the data
AOdata = dfao.to_csv('Sweep AO data.csv')

# %%Extract the "X_wfm" array
x_array = [entry['Y'] for entry in data['result']['X_wfm']]

# %%Convert to DataFrame
dfx = pd.DataFrame(x_array).transpose()

#%%Printing the data
print(dfx)

#%%Saving the data
Xdata = dfx.to_csv('Sweep X data.csv')

# %%Extract the "Y_wfm" array
y_array = [entry['Y'] for entry in data['result']['Y_wfm']]

# %%Convert to DataFrame
dfy = pd.DataFrame(y_array).transpose()

#%% Printing dfy
print(dfy)

#%%Saving the data
Ydata = dfy.to_csv('Sweep Y data.csv')

# %% Plotting AO_wfm
plt.plot(dfao)
plt.title('Sweep AO')
plt.xlabel('Samples')
plt.ylabel('Sweep AO (V)')
plt.show()
plt.savefig("Sweep AO.png", dpi=500)

# %% Plotting AI_wfm
plt.plot(dfai)
plt.title('Sweep AI')
plt.xlabel('Samples')
plt.ylabel('Sweep AI (V)')
plt.show()
plt.savefig("Sweep AI.png", dpi=500)


# %% Plotting X_wfm
plt.plot(dfx)
plt.title('Sweep X')
plt.xlabel('Samples')
plt.ylabel('Sweep X Results (V)')
plt.show()
plt.savefig("Sweep X.png", dpi=500)


# %%Plotting Y_wfm
plt.plot(dfy)
plt.title('Sweep Y')
plt.xlabel('Samples')
plt.ylabel('Sweep Y Results (V)')
plt.show()
plt.savefig("Sweep Y.png", dpi=500)



# %%
