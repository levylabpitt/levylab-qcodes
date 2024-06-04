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

class PPMSSim(ZMQInstrument):
    """
    Class to represent the PPMS in LevyLab Instrument Framework
    This is a child class of ZMQInstrument, which is a child class of Instrument.

    This driver talks to the PPMS Monitor and Control software via ZMQ.

    Args:
        name: The name used internally by QCoDeS for this driver
        address: The ZMQ server address.
          E.g. 'tcp://localhost:29270' for simulated PPMS
    """

    def __init__(self, name: str, address: str, **kwargs: Any) -> None:
        super().__init__(name=name, address=address, **kwargs)


        self.add_parameter('temperature',
                           label='Temperature',
                           unit='K',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._temp_setter,
                           get_cmd=partial(self._temp_getter, 'Temperature (K)'))
        # Issue: A parameter is usually a single value, but here we have a list of values.
        # We should be able to specify each of these separately.

        self.add_parameter('temperature_state',
                           label='Temperature State',
                           get_cmd=partial(self._temp_getter, 'Temperature Status'))

        self.add_parameter('field',
                           label='B Field',
                           unit='T',
                           set_cmd=self._field_setter,
                           get_cmd=partial(self._field_getter, 'Field (T)'))

        self.add_parameter('magnet_state',
                           label='Magnet State',
                           get_cmd=partial(self._field_getter, 'Magnet Status'))

        self.print_readable_snapshot(update=True)
        self.connect_message()

    def _temp_getter(
        self,
        param_name: Literal[
            "Temperature (K)", "Temperature Status",
        ],
    ) -> Union[int, float]:
        raw_response = self._send_command('Get Temperature')
        response = raw_response['result'][param_name]
        return response

    def _temp_setter(
        self,
        temp_params,
    ) -> None:
        param = {'Temperature (K)': temp_params[0], 
                 'Rate (K/min)': temp_params[1]}
        self._send_command('Set Temperature', param)
        print(f"Setting temperature to {temp_params[0]} K at {temp_params[1]} K/min")
        # feedback
        while not self._is_temperature_set(temp_params[0]):
            sleep(1)
        print(f"Temperature set to {temp_params[0]} K")

    def _is_temperature_set(self, target_temp):
        current_temp = self._temp_getter('Temperature (K)')
        if current_temp is not None:
            return current_temp == target_temp
        return False

    def _field_getter(
        self,
        param_name: Literal[
            "Field (T)", "Magnet Status",
        ],
    ) -> Union[int, float]:
        raw_response = self._send_command('Get Magnet')
        response = raw_response['result'][param_name]
        return response

    def _field_setter(
        self,
        field_params,
    ) -> None:
        param = {'Field (T)': field_params[0], 
                 'Rate (T/min)': field_params[1]}
        self._send_command('Set Magnet', param)

        print(f"Setting B field to {field_params[0]} T at {field_params[1]} T/min")
        # feedback
        while not self._is_field_set(field_params[0]):
            sleep(1)
        print(f"B Field set to {field_params[0]} K")

    def _is_field_set(self, target_field):
        current_field = self._field_getter('Field (T)')
        if current_field is not None:
            return current_field == target_field
        return False
    
if __name__ == '__main__':
    """
    Test the PPMS class
    """
    from qcodes.logger import start_all_logging
    start_all_logging()
    ppms = PPMSSim('ppms', 'tcp://localhost:29270')
    ppms.close()