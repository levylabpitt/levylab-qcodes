import levylabinst
import json
import warnings
from functools import partial
from time import sleep
from typing import Any, Callable, ClassVar, Literal, Optional, Union, cast
from matplotlib.pylab import set_state
import zmq
import numpy as np
import qcodes.validators as vals
from qcodes.utils import DelayedKeyboardInterrupt
import time
import tkinter as tk
import matplotlib.pyplot as plt
import pandas as pd
from .ZMQInstrument import ZMQInstrument
from tkinter import simpledialog, messagebox
from typing import Any, Dict
from levylabinst import MCLockin



class Experiments(MCLockin):
    """
    This class contains the functions which correspond to different sweeping experiments.
    """
    def _data_sweepX1(self) -> None:
        """
        This function will give the sweep results X (V) data after the sweep is completed.
        """
        data = self._get_sweep_data()
        x_array = [entry['Y'] for entry in data['result']['X_wfm']]
        dfx = pd.DataFrame(x_array).transpose()
        xai1 = dfx[0]
        return xai1
    
    def _sweep_2d_X1(self, extra_dimension: list,  channel_configs: list, initial_wait: float, sweep_time: float) -> None:
        """
        This function will perform multiple 1-dimensional sweeps for each values of external parameter. The external parameter
        is considered as an extra-dimension, and thus this type of sweep is called as "2-dimensional sweep".
        """
        X1  = []
        for values in extra_dimension:
            self._set_1dsweepconfig(channel_configs, initial_wait, sweep_time)
            self._sweep_process()
            x1 = self._data_sweepX1()
            x1array = np.array(x1)
            X1.append(x1array)
        return X1



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

    