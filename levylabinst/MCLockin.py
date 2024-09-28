import json
import warnings
from functools import partial
from time import sleep
from typing import Any, Callable, ClassVar, Literal, Optional, Union, cast
import zmq
import numpy as np
import os   # Check if the config file exists
from .ZMQInstrument import ZMQInstrument
import qcodes.validators as vals
from qcodes.utils import DelayedKeyboardInterrupt
import time
import tkinter as tk
from tkinter import simpledialog, messagebox
from typing import Any, Dict
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ConfigChangeHandler(FileSystemEventHandler):
    def __init__(self, lockin_instance):
        self.lockin_instance = lockin_instance

    def on_modified(self, event):
        if event.src_path.endswith(self.lockin_instance.config_file):
            print(f"Detected changes in {self.lockin_instance.config_file}, reloading config ...")
            self.lockin_instance.reload_config()

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

    def __init__(self, name: str, address: str, config_file: str = 'experiment.config.json', **kwargs: Any) -> None:
        super().__init__(name=name, address=address,**kwargs)
        self.config_file = config_file
        self.config = self._get_config_from_file(config_file)
        self._ref_channel = 1

        # Start the file watcher for the config file
        self.start_file_watcher()

        for label, value in self.config['lockin_config_info'].items():
            self.add_parameter(f'{label}_Amp',
                               label=f'{label} Amplitude',
                               unit='V',
                               vals=vals.Numbers(0, 100),
                               get_cmd=self._dump,
                               set_cmd=partial(self._set_amplitude, value))
            
            self.add_parameter(f'{label}_DC',
                               label=f'{label} DC',
                               unit='V',
                               vals=vals.Numbers(0, 100),
                               get_cmd=self._dump,
                               set_cmd=partial(self._set_dc, value))
            
            self.add_parameter(f'{label}_Freq',
                               label=f'{label} Frequency',
                               unit='Hz',
                               vals=vals.Numbers(0, 100),
                               get_cmd=self._dump,
                               set_cmd=partial(self._set_freq, value))
            
            self.add_parameter(f'{label}_Phase',
                               label=f'{label} Phase',
                               unit='deg',
                               vals=vals.Numbers(0, 100),
                               get_cmd=self._dump,
                               set_cmd=partial(self._set_phase, value))
            
            self.add_parameter(f'{label}_Function',
                               label=f'{label} Function',
                               unit='',
                               vals=vals.Enum('Sine', 'Square', 'Triangle'),
                               get_cmd=self._dump,
                               set_cmd=partial(self._set_func, value))
            
            Measurements = ['X', 'Y', 'R', 'Theta', 'Mean']
            for measurement in Measurements:
                meas_unit = 'deg' if measurement == 'Theta' else 'V'
                self.add_parameter(f'{label}_{measurement}',
                                   label=f'{label} {measurement}',
                                   unit=meas_unit,
                                   get_cmd=partial(self._get_lockin, measurement, value))
            
        self.add_parameter('state',
                            label='Lockin State',
                            unit='',
                            vals=vals.Enum('start', 'start sweep', 'stop sweep', 'stop'),
                            get_cmd=self._dump,
                            set_cmd=self._set_state)
            
        # self.print_readable_snapshot(update=True)
        self.connect_message()

    def reset_parameters(self):
        """
        Reset defined channel parameters in JSON to default values:
        - Amplitude: 0 V
        - DC: 0 V
        - Frequency: 0 Hz
        - Phase: 0 degrees
        - Function: Sine
        """
        default_values = {
            'Amp': 0,
            'DC': 0,
            'Freq': 0,
            'Phase': 0,
            'Function': 'Sine'
        }

        for label, value in self.config['lockin_config_info'].items():
            self.set(f'{label}_Amp', default_values['Amp'])
            self.set(f'{label}_DC', default_values['DC'])
            self.set(f'{label}_Freq', default_values['Freq'])
            self.set(f'{label}_Phase', default_values['Phase'])
            self.set(f'{label}_Function', default_values['Function'])

        print("Parameters for defined channels have been reset to default values.")

    def reset_all_parameters(self) -> None:
        """
        Reset all 8 channels to default values:
        Amplitude = 0 V, DC = 0 V, Frequency = 0 Hz, Phase = 0 degrees, Function = Sine.
        """
        default_values = {
            'Amplitude (V)': 0,
            'DC (V)': 0,
            'Frequency (Hz)': 0,
            'Phase (deg)': 0,
            'Function': 'Sine'
        }

        # Reset parameters for all 8 channels (channel numbers 1 to 8)
        for channel in range(1, 9):
            self._send_command('setAO_Amplitude', {'AO Channel': channel, 'Amplitude (V)': default_values['Amplitude (V)']})
            self._send_command('setAO_DC', {'AO Channel': channel, 'DC (V)': default_values['DC (V)']})
            self._send_command('setAO_Frequency', {'AO Channel': channel, 'Frequency (Hz)': default_values['Frequency (Hz)']})
            self._send_command('setAO_Phase', {'AO Channel': channel, 'Phase (deg)': default_values['Phase (deg)']})
            self._send_command('setAO_Function', {'AO Channel': channel, 'Function': default_values['Function']})

        print("All 8 channels have been reset to default values.")

    def reload_config(self):
        """
        Reload the configuration from the JSON file and update channels.
        """
        try:
            new_config = self._get_config_from_file(self.config_file)

            existing_channels = set(self.config['lockin_config_info'].keys())
            new_channels = set(new_config['lockin_config_info'].keys())

            for channel in existing_channels - new_channels:
                del self.parameters[f'{channel}_Amp']
                del self.parameters[f'{channel}_DC']
                del self.parameters[f'{channel}_Freq']
                del self.parameters[f'{channel}_Phase']
                del self.parameters[f'{channel}_Function']

            for channel in new_channels & existing_channels:
                del self.parameters[f'{channel}_Amp']
                del self.parameters[f'{channel}_DC']
                del self.parameters[f'{channel}_Freq']
                del self.parameters[f'{channel}_Phase']
                del self.parameters[f'{channel}_Function']

            #for channel in new_channels - existing_channels:
            #    self.add_channel(channel, new_config['lockin_config_info'][channel])

            #for channel in existing_channels - new_channels:
            #    self.remove_channel(channel)

            self.config = new_config

            # Reinitialize parameters
            for label, value in self.config['lockin_config_info'].items():
                self.add_parameter(f'{label}_Amp',
                               label=f'{label} Amplitude',
                               unit='V',
                               vals=vals.Numbers(0, 100),
                               get_cmd=self._dump,
                               set_cmd=partial(self._set_amplitude, value))
            
                self.add_parameter(f'{label}_DC',
                               label=f'{label} DC',
                               unit='V',
                               vals=vals.Numbers(0, 100),
                               get_cmd=self._dump,
                               set_cmd=partial(self._set_dc, value))
            
                self.add_parameter(f'{label}_Freq',
                               label=f'{label} Frequency',
                               unit='Hz',
                               vals=vals.Numbers(0, 100),
                               get_cmd=self._dump,
                               set_cmd=partial(self._set_freq, value))
            
                self.add_parameter(f'{label}_Phase',
                               label=f'{label} Phase',
                               unit='deg',
                               vals=vals.Numbers(0, 100),
                               get_cmd=self._dump,
                               set_cmd=partial(self._set_phase, value))
            
                self.add_parameter(f'{label}_Function',
                               label=f'{label} Function',
                               unit='',
                               vals=vals.Enum('Sine', 'Square', 'Triangle'),
                               get_cmd=self._dump,
                               set_cmd=partial(self._set_func, value))

            print("Config reloaded successfully.")
        except Exception as e:
            print(f"Failed to reload configuration: {e}")

    def start_file_watcher(self):
        """
        Start watching {self.config_file} for changes.
        """

        event_handler = ConfigChangeHandler(self)
        observer = Observer()
        config_dir = os.path.dirname(os.path.abspath(self.config_file))
        observer.schedule(event_handler, path= config_dir, recursive= False)
        observer.start()
        print(f"Started watching {self.config_file} for changes.")
        # Run the observer in a separate thread to avoid blocking
        import threading
        threading.Thread(target=observer.join).start()

    def _get_config_from_file(self, config_file: str) -> Dict[str, int]:
        """
        Reads configuration from an external JSON file.

        Returns:
            config (dict): A dictionary with labels as keys and lead numbers as values.
        """
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"{config_file} not found. Please provide the correct path.")

        with open(config_file, 'r') as file:
            config = json.load(file)

        return config
    
    def dashboard(self):
        """
        Launches a dashboard where the user can view existing channels, 
        add new channels, 
        delete channels,
        and view experiment info.
        """
        # Load information from the config file
        config_data = self._get_config_from_file(self.config_file)
        wirebonding_info = config_data.get('wirebonding_info', 'No info available')
        krohn_hite_info = config_data.get('krohn_hite_info', 'No info available')
        experiment_note_info = config_data.get('experiment_note_info', 'No info available')
        
        # Create the dashboard window
        dashboard = tk.Tk()
        dashboard.title("Experiment Dashboard")

        # Function to update the dashboard with the current channels and additional info
        def update_dashboard():
            
            #Clear all existing widgets from the window before refreshing
            for widget in dashboard.grid_slaves():
                widget.grid_forget()

            # Display the existing channels in the config
            tk.Label(dashboard, text="Existing Channels:").grid(row=0, column=0, columnspan=2)

            row = 1
            for label, lead_number in self.config['lockin_config_info'].items():
                tk.Label(dashboard, text=f"Channel {label}:").grid(row=row, column=0)
                tk.Label(dashboard, text=f"Lead Number {lead_number}").grid(row=row, column=1)
                row += 1

            # Display wirebonding details
            tk.Label(dashboard, text="WireBonding Info:").grid(row=row, column=0, sticky="w")
            tk.Label(dashboard, text=wirebonding_info).grid(row=row, column=1, sticky="w")
            row += 1

            # Display krohn-hite details
            tk.Label(dashboard, text="Krohn-Hite Info:").grid(row=row, column=0, sticky="w")
            tk.Label(dashboard, text=krohn_hite_info).grid(row=row, column=1, sticky="w")
            row += 1

            # Display experiment notes
            tk.Label(dashboard, text="Experiment Note:").grid(row=row, column=0, sticky="w")
            tk.Label(dashboard, text=experiment_note_info).grid(row=row, column=1, sticky="w")
            row += 1

            # OK button to close the dashboard
            ok_button = tk.Button(dashboard, text="OK", command=dashboard.destroy)
            ok_button.grid(row=row + 1, column=0, columnspan=2)

        # Initially update the dashboard when the window is created
        update_dashboard()

        # Start the dashboard main loop
        dashboard.mainloop()

    
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
    
    def _set_state(self, value: str) -> None:
        param = value
        self._send_command('setState', param)
    
    def _set_sweepTime(self, value: float) -> None:
        param = value
        self._send_command('setSweepTime', param)
        
    def _set_sweepconfig(self, channel: int, start: float, stop: float, pattern: str, initial_wait: float, sweep_time: float, ) -> None:
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
    print("Starting MCLockin...")
    lockin = MCLockin('lockin', 'tcp://localhost:29170', config_file=os.path.abspath('D:\\Code\\Github\\levylab-qcodes\\tests\\experiment.config.json'))
    print("Launching dashboard...")
    lockin.dashboard()
    print("Closing MCLockin...")
    lockin.close()