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

# %%defining functions
lockin._set_sweepconfig(1,0.04,0.09,"Ramp /",5,9)
lockin._set_state('start sweep')
time.sleep(12) #To make sure, the sweeping is done completely. The sleep time is more than sweeping time.
data=lockin._get_sweep_data() 

#%%Making into a csv file
#sdata= pd.DataFrame(data)

# %%Saving data into .csv files
#sdata.to_csv('sweep dataset.csv', index=False)
#print(data) 

# %%Extract the "AI_wfm" array
ai_array = data['result']['AI_wfm'][0]['Y']

# %%Convert to DataFrame
dfai = pd.DataFrame(ai_array, columns=['Y'])


# %%Extract the "AO_wfm" array
ao_array = data['result']['AO_wfm'][0]['Y']

# %%Convert to DataFrame
dfao = pd.DataFrame(ao_array, columns=['Y'])

# %%Extract the "X_wfm" array
x_array = data['result']['X_wfm'][0]['Y']

# %%Convert to DataFrame
dfx = pd.DataFrame(x_array, columns=['Y'])

# %%Display the DataFrame
#print(df)

# %% Plotting AO_wfm
plt.plot(dfai['Y'])
plt.title('Waveform Data')
plt.xlabel('Index')
plt.ylabel('Amplitude')
plt.show()