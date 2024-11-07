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
    

