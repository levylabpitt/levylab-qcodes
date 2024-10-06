import json
import warnings
from functools import partial
from time import sleep
from typing import Any, Callable, ClassVar, Literal, Optional, Union, cast
from matplotlib.pylab import set_state
import zmq
import numpy as np
from .ZMQInstrument import ZMQInstrument
import qcodes.validators as vals
from qcodes.utils import DelayedKeyboardInterrupt
import time
import tkinter as tk
import matplotlib.pyplot as plt
import pandas as pd
from tkinter import simpledialog, messagebox
from typing import Any, Dict

class MCLockin(ZMQInstrument):
    """
    Class to represent the Multichannel Lock-in in LevyLab Instrument Framework
    This is a child class of ZMQInstrument, which is a child class of Instrument.

    This driver talks to the PPMS Monitor and Control software via ZMQ.

    Args:
        name: The name used internally by QCoDeS for this driver
        address: The ZMQ server address.
            E.g. 'tcp://localhost:29170' for the MC Lock-in
        config: A dictionary of the channel configuration parameters for the lock-in
            E.g. {'Ip': 1, 'Im': 2, 'Vp': 3, 'Vm': 4}
    """

    def __init__(self, name: str, address: str, config:dict, **kwargs: Any) -> None:
        super().__init__(name=name, address=address,**kwargs)
        if config is None:
            config = self._get_config_from_gui()

        self.config = config
        # Define the parameters for the lock-in experiment (specific to the experiment)
        # self.drain_channel = 1
        # self.drain_ref = 1
        # self.drain_measurement = 'X'
        self._ref_channel = 1

        for label, value in config.items():
            self.add_parameter(f'{label}_Amp',
                               label=f'{label} Amplitude',
                               unit='V',
                               vals=vals.Numbers(0, 100),
                               get_cmd=self._dump,
                               set_cmd=partial(self._set_amplitude, config[label]))
            
            self.add_parameter(f'{label}_DC',
                               label=f'{label} DC',
                               unit='V',
                               vals=vals.Numbers(0, 100),
                               get_cmd=self._dump,
                               set_cmd=partial(self._set_dc, config[label]))
            
            self.add_parameter(f'{label}_Freq',
                               label=f'{label} Frequency',
                               unit='Hz',
                               vals=vals.Numbers(0, 100),
                               get_cmd=self._dump,
                               set_cmd=partial(self._set_freq, config[label]))
            
            self.add_parameter(f'{label}_Phase',
                               label=f'{label} Phase',
                               unit='deg',
                               vals=vals.Numbers(0, 100),
                               get_cmd=self._dump,
                               set_cmd=partial(self._set_phase, config[label]))
            
            self.add_parameter(f'{label}_Function',
                               label=f'{label} Function',
                               unit='',
                               vals=vals.Enum('Sine', 'Square', 'Triangle'),
                               get_cmd=self._dump,
                               set_cmd=partial(self._set_func, config[label]))
            
            Measurements = ['X', 'Y', 'R', 'Theta', 'Mean']
            for measurement in Measurements:
                meas_unit = 'deg' if measurement == 'Theta' else 'V'
                self.add_parameter(f'{label}_{measurement}',
                                   label=f'{label} {measurement}',
                                   unit=meas_unit,
                                   get_cmd=partial(self._get_lockin, measurement, config[label]))
            
        self.add_parameter('state',
                            label='Lockin State',
                            unit='',
                            vals=vals.Enum('start', 'start sweep', 'stop', 'stop sweep'),
                            get_cmd=self._get_state,
                            set_cmd=self._set_state)
            
        # self.print_readable_snapshot(update=True)
        self.connect_message()

    def _get_config_from_gui(self) -> Dict[str, int]:
        """
        Opens a GUI to prompt the user for channel configuration.
        Returns:
            config (dict): A dictionary with labels as keys and lead numbers as values.
        """
        config = {}

        # Create the tkinter root window
        root = tk.Tk()
        root.title("Channel Configuration")

        label_entries = []
        lead_entries = []
        
        def generate_fields():
            nonlocal label_entries, lead_entries
            # Clear any previous entries if they exist
            for widget in root.grid_slaves():
                if int(widget.grid_info()["row"]) > 1:
                    widget.grid_forget()

            try:
                # Get the number of channels
                num_channels = int(num_channels_entry.get())

                # Create new input fields based on the number of channels
                label_entries = []
                lead_entries = []

                for i in range(num_channels):
                    # Create label and entry for each channel's label
                    tk.Label(root, text=f"Channel {i + 1} Label:").grid(row=i + 2, column=0)
                    label_entry = tk.Entry(root)
                    label_entry.grid(row=i + 2, column=1)
                    label_entries.append(label_entry)

                    # Create label and entry for each channel's lead number
                    tk.Label(root, text=f"Channel {i + 1} Lead Number:").grid(row=i + 2, column=2)
                    lead_entry = tk.Entry(root)
                    lead_entry.grid(row=i + 2, column=3)
                    lead_entries.append(lead_entry)

                # Enable the submit button after fields are generated
                submit_button.config(state=tk.NORMAL)

            except ValueError:
                messagebox.showerror("Input Error", "Please enter a valid integer for the number of channels.")
        
        def on_submit():
            try:
                for i in range(len(label_entries)):
                    label = label_entries[i].get()
                    lead_number = int(lead_entries[i].get())
                    config[label] = lead_number
                root.destroy()  # Close the GUI window after submitting
            except ValueError:
                messagebox.showerror("Input Error", "Lead numbers must be integers.")

        # Instruction Label
        tk.Label(root, text="Enter the number of channels:").grid(row=0, column=0)

        # Entry field for the number of channels
        num_channels_entry = tk.Entry(root)
        num_channels_entry.grid(row=0, column=1)

        # Button to generate input fields
        generate_button = tk.Button(root, text="Generate Fields", command=generate_fields)
        generate_button.grid(row=0, column=2)

        # Submit button (initially disabled, enabled after fields are generated)
        submit_button = tk.Button(root, text="Submit", command=on_submit)
        submit_button.grid(row=1, column=1)
        submit_button.config(state=tk.DISABLED)  # Disable submit button initially

        # Start the tkinter main loop
        root.mainloop()

        return config
    
    def get_idn(self) -> dict[str, Optional[str]]:
        """
        This is a temporary override. It should go in the ZMQInstrument class. and called by Inst Framework by a RPC call.
        """
        return {
            "vendor": "LevyLab",
            "model": "MC Lock-in",
            "serial": None,
            "firmware": "v2.15.4.4",
        }
    def _dump(self):
        pass

    def _set_amplitude(self, channel: int, value: float) -> None:
        param = {'AO Channel': channel, 'Amplitude (V)': value}
        self._send_command('setAO_Amplitude', param)

    def _set_dc(self, channel: int, value: float) -> None:
        param = {'AO Channel': channel, 'DC (V)': value}
        self._send_command('setAO_DC', param)

    def _set_freq(self, channel: int, value: float) -> None:
        param = {'AO Channel': channel, 'Frequency (Hz)': value}
        self._send_command('setAO_Frequency', param)

    def _set_phase(self, channel: int, value: float) -> None:
        param = {'AO Channel': channel, 'Phase (deg)': value}
        self._send_command('setAO_Phase', param)

    def _set_func(self, channel: int, value: str) -> None:
        param = {'AO Channel': channel, 'Function': value}
        self._send_command('setAO_Function', param)
    
    def _get_lockin(self, value: str, channel: int) -> float:
        key = f"AI{channel}.Ref{self._ref_channel}.{value}"
        response = self._send_command('getResults')
        results = response['result']['Results (Dictionary)']
        results_dict = {item['key']: item['value'] for item in results}
        return results_dict.get(key)
    
    def _get_sweep_data(self) -> dict: #this function will get the data from the lockin afte sweeping is done. It is based on the API "getsweepdata.VI". All the data from labview are being stored as dictionary (dict).
        response = self._send_command('getSweepWaveforms')
        return response
    
    def _get_state(self) -> dict:
        response = self._send_command('getState')
        return response['result']
    
    def _set_state(self, value: str) -> None:
        param = value
        self._send_command('setState', param)
    
    def _set_sweepTime(self, value: float) -> None:
        param = value
        self._send_command('setSweepTime', param)

    def _get_AO(self) -> dict:
        response = self._send_command('getAOconfig')
        return response
    
    def _sweep_process_duration(self, swtime = float) -> None: #To process the sweeping during given sweeping time 
        time.sleep(swtime)

    def _sweep_checking(self) -> None:
         while self._get_state() == 'sweeping':
             time.sleep(0.2) 

    def _plot_SweepAI(self) -> None:
        data = self._get_sweep_data()
        ai_array = [entry['Y'] for entry in data['result']['AI_wfm']]
        dfai = pd.DataFrame(ai_array).transpose()
        print(dfai)
        dfai.to_csv('Sweep AI data.csv')
        plt.plot(dfai)
        plt.title('Sweep AI')
        plt.xlabel('Samples')
        plt.ylabel('Sweep AI (V)')
        plt.show()
        plt.savefig("Sweep AI.png", dpi=500)

    def _plot_SweepAO(self) -> None:
        data = self._get_sweep_data()
        ao_array = [entry['Y'] for entry in data['result']['AO_wfm']]
        dfao = pd.DataFrame(ao_array).transpose()
        print(dfao)
        dfao.to_csv('Sweep AO data.csv')
        plt.plot(dfao)
        plt.title('Sweep AO')
        plt.xlabel('Samples')
        plt.ylabel('Sweep AO (V)')
        plt.show()
        plt.savefig("Sweep AO.png", dpi=500)

    def _plot_SweepY(self) -> None:
        data = self._get_sweep_data()
        y_array = [entry['Y'] for entry in data['result']['Y_wfm']]
        dfy = pd.DataFrame(y_array).transpose()
        print(dfy)
        dfy.to_csv('Sweep Y data.csv')
        plt.plot(dfy)
        plt.title('Sweep Y')
        plt.xlabel('Samples')
        plt.ylabel('Sweep Y results (V)')
        plt.show()
        plt.savefig("Sweep Y.png", dpi=500)

    def _plot_SweepX(self) -> None:
        data = self._get_sweep_data()
        x_array = [entry['Y'] for entry in data['result']['X_wfm']]
        dfx = pd.DataFrame(x_array).transpose()
        print(dfx)
        dfx.to_csv('Sweep X data.csv')
        plt.plot(dfx)
        plt.title('Sweep X')
        plt.xlabel('Samples')
        plt.ylabel('Sweep X results (V)')
        plt.show()
        plt.savefig("Sweep X.png", dpi=500)

    

    def _set_sweepconfig(self, channel: int, start: float, stop: float, pattern: str, initial_wait: float, sweep_time: float) -> None:
        '''
        Sets the sweep configuration for the lock-in
        Currently only supports one channel
        Args:
            channel: The channel to set the sweep configuration for
            start: The start time of the sweep
            stop: The stop time of the sweep
            sweep_time: The time of the sweep
            pattern: The pattern of the sweep
        '''
        if pattern == "Table":
           param = {"Sweep Time (s)":sweep_time,
                 "Initial Wait (s)":initial_wait,
                 "Return to Start":False,
                 "Channels":[{"Enable?":True,
                              "Channel":channel,
                              "Start":start,
                              "End":stop,
                              "Pattern": pattern,
                              "Table": [2,4,6,8]}]} 
        else:
            param = {"Sweep Time (s)":sweep_time,
                 "Initial Wait (s)":initial_wait,
                 "Return to Start":False,
                 "Channels":[{"Enable?":True,
                              "Channel":channel,
                              "Start":start,
                              "End":stop,
                              "Pattern": pattern,
                              "Table":[]}]}      
        self._send_command('setSweep', param)

if __name__ == '__main__':
    """
    Test the Lockin class
    """
    from qcodes.logger import start_all_logging
    start_all_logging()
    lockin = MCLockin('lockin', 'tcp://localhost:29170')
    lockin.close()


