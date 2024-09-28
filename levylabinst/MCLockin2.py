import json
import warnings
from functools import partial
from time import sleep
from typing import Any, Callable, ClassVar, Literal, Optional, Union, cast
import zmq
import numpy as np
from .ZMQInstrument import ZMQInstrument
import qcodes.validators as vals
from qcodes.utils import DelayedKeyboardInterrupt
import time

class MCLockin2(ZMQInstrument):
    """
    Class to represent the Multichannel Lock-in in LevyLab Instrument Framework
    This is a child class of ZMQInstrument, which is a child class of Instrument.

    This driver talks to the Multichannel Lock-in software via ZMQ.

    Args:
        name: The name used internally by QCoDeS for this driver
        address: The ZMQ server address.
          E.g. 'tcp://localhost:29170' for the MC Lock-in
    """

    def __init__(self, name: str, address: str, **kwargs: Any) -> None:
        super().__init__(name=name, address=address, **kwargs)

        # Define the parameters for the lock-in experiment (specific to the experiment)
        self.drain_channel = 1
        self.drain_ref = 1
        self.drain_measurement = 'X'

        # We can probably configure the lockin at the class instantiation
        # define I+ and I- channels etc.

        self.add_parameter('gate',
                           label='Gate Voltage',
                           unit='V',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._gate_channel_setter,
                           set_cmd2= self._gate_voltage_setter, #sweeping channel no. "" with gate voltage "" volt.
                           get_cmd=self._gate_getter)
        
        self.add_parameter('drain',
                           label='Drain Voltage',
                           unit='V',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._drain_setter,
                           get_cmd=self._drain_getter)
        

        self.print_readable_snapshot(update=True)
        self.connect_message()

    def get_idn(self) -> dict[str, Optional[str]]:
        """
        This is a temporary override. It should go in the ZMQInstrument class.
        """
        return {
            "vendor": "LevyLab",
            "model": "MC Lock-in",
            "serial": None,
            "firmware": "v2.15.4.4",
        }

    def _gate_getter(self):
        pass

    def _gate_channel_setter(self,AOvalue) -> None:
        param = {'AO Channel': AOvalue}
        self._send_command('setAO_DC', param)

    def _gate_voltage_setter(self,GVvalue) -> None:
        param = {'DC (V)': GVvalue}
        self._send_command('DC (V)', param)    

    def _drain_getter(self):
        key = f"AI{self.drain_channel}.Mean" if self.drain_measurement == 'Mean' else f"AI{self.drain_channel}.Ref{self.drain_ref}.{self.drain_measurement}"

        response = self._send_command('getResults')
        results = response['result']['Results (Dictionary)']
        results_dict = {item['key']: item['value'] for item in results}
        return results_dict.get(key)

    def _drain_setter(self, value) -> None:
        pass
    

    
if __name__ == '__main__':
    """
    Test the Lockin class
    """
    from qcodes.logger import start_all_logging
    start_all_logging()
    lockin = MCLockin('lockin', 'tcp://localhost:29170')
    lockin.close()