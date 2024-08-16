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


class MCLockin(ZMQInstrument):
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
                           set_cmd=self._gate_setter,
                           get_cmd=self._gate_getter)
        
        self.add_parameter('drain',
                           label='Drain Voltage',
                           unit='V',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._drain_setter,
                           get_cmd=self._drain_getter)

        self.add_parameter('source',
                           label='Source Amp',
                           unit='V',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._source_setter,
                           get_cmd=self._source_getter)
        
        self.add_parameter('frequency1',
                    label='Source frequency',
                    unit='Hz',
                    set_cmd=lambda x: self._frequency_setter(channel=1, x),
                    get_cmd=self._frequency_getter,)

        self.add_parameter('frequency2',
                           label='Source frequency',
                           unit='Hz',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._frequency2_setter,
                           get_cmd=self._frequency_getter)

        self.add_parameter('frequency3',
                           label='Source frequency',
                           unit='Hz',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._frequency3_setter,
                           get_cmd=self._frequency_getter)

        self.add_parameter('frequency4',
                           label='Source frequency',
                           unit='Hz',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._frequency4_setter,
                           get_cmd=self._frequency_getter)

        self.add_parameter('frequency5',
                           label='Source frequency',
                           unit='Hz',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._frequency5_setter,
                           get_cmd=self._frequency_getter)

        self.add_parameter('frequency6',
                           label='Source frequency',
                           unit='Hz',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._frequency6_setter,
                           get_cmd=self._frequency_getter)

        self.add_parameter('frequency7',
                           label='Source frequency',
                           unit='Hz',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._frequency7_setter,
                           get_cmd=self._frequency_getter)

        self.add_parameter('frequency8',
                           label='Source frequency',
                           unit='Hz',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._frequency8_setter,
                           get_cmd=self._frequency_getter)

        self.add_parameter('amplitude1',
                           label='amplitude',
                           unit='V',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._amplitude1_setter,
                           get_cmd=self._amplitude_getter)

        self.add_parameter('amplitude2',
                           label='amplitude',
                           unit='V',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._amplitude2_setter,
                           get_cmd=self._amplitude_getter)

        self.add_parameter('amplitude3',
                           label='amplitude',
                           unit='V',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._amplitude3_setter,
                           get_cmd=self._amplitude_getter)

        self.add_parameter('amplitude4',
                           label='amplitude',
                           unit='V',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._amplitude4_setter,
                           get_cmd=self._amplitude_getter)

        self.add_parameter('amplitude5',
                           label='amplitude',
                           unit='V',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._amplitude5_setter,
                           get_cmd=self._amplitude_getter)

        self.add_parameter('amplitude6',
                           label='amplitude',
                           unit='V',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._amplitude6_setter,
                           get_cmd=self._amplitude_getter)

        self.add_parameter('amplitude7',
                           label='amplitude',
                           unit='V',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._amplitude7_setter,
                           get_cmd=self._amplitude_getter)

        self.add_parameter('amplitude8',
                           label='amplitude',
                           unit='V',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._amplitude8_setter,
                           get_cmd=self._amplitude_getter)

        self.add_parameter('DC1',
                           label='DC',
                           unit='V',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._DC1_setter,
                           get_cmd=self._DC_getter)

        self.add_parameter('DC2',
                           label='DC',
                           unit='V',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._DC2_setter,
                           get_cmd=self._DC_getter)

        self.add_parameter('DC3',
                           label='DC',
                           unit='V',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._DC3_setter,
                           get_cmd=self._DC_getter)

        self.add_parameter('DC4',
                           label='DC',
                           unit='V',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._DC4_setter,
                           get_cmd=self._DC_getter)

        self.add_parameter('DC5',
                           label='DC',
                           unit='V',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._DC5_setter,
                           get_cmd=self._DC_getter)

        self.add_parameter('DC6',
                           label='DC',
                           unit='V',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._DC6_setter,
                           get_cmd=self._DC_getter)

        self.add_parameter('DC7',
                           label='DC',
                           unit='V',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._DC7_setter,
                           get_cmd=self._DC_getter)

        self.add_parameter('DC8',
                           label='DC',
                           unit='V',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._DC8_setter,
                           get_cmd=self._DC_getter)

        self.add_parameter('phase1',
                           label='phase',
                           unit='°',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._phase1_setter,
                           get_cmd=self._phase_getter)

        self.add_parameter('phase2',
                           label='phase',
                           unit='°',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._phase2_setter,
                           get_cmd=self._phase_getter)

        self.add_parameter('phase3',
                           label='phase',
                           unit='°',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._phase3_setter,
                           get_cmd=self._phase_getter)

        self.add_parameter('phase4',
                           label='phase',
                           unit='°',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._phase4_setter,
                           get_cmd=self._phase_getter)

        self.add_parameter('phase5',
                           label='phase',
                           unit='°',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._phase5_setter,
                           get_cmd=self._phase_getter)

        self.add_parameter('phase6',
                           label='phase',
                           unit='°',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._phase6_setter,
                           get_cmd=self._phase_getter)

        self.add_parameter('phase7',
                           label='phase',
                           unit='°',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._phase7_setter,
                           get_cmd=self._phase_getter)

        self.add_parameter('phase8',
                           label='phase',
                           unit='°',
                        #    vals=vals.Numbers(1.6, 400),
                           set_cmd=self._phase8_setter,
                           get_cmd=self._phase_getter)

        
        

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

    def _gate_setter(self,value) -> None:
        param = {'AO Channel': 2, 'DC (V)': value}
        self._send_command('setAO_DC', param)

    def _source_setter(self,value) -> None:
        param = {'AO Channel': 1, 'Amplitude (V)': value}
        self._send_command('setAO_Amplitude', param)

    def _source_getter(self) -> None:
        pass

    def _frequency1_setter(self,value) -> None:
        param = {'AO Channel': 1, 'Frequency (Hz)':value}
        self._send_command('setAO_Frequency',param)

    def _frequency2_setter(self,value) -> None:
        param = {'AO Channel': 2, 'Frequency (Hz)':value}
        self._send_command('setAO_Frequency',param)

    def _frequency3_setter(self,value) -> None:
        param = {'AO Channel': 3, 'Frequency (Hz)':value}
        self._send_command('setAO_Frequency',param)

    def _frequency4_setter(self,value) -> None:
        param = {'AO Channel': 4, 'Frequency (Hz)':value}
        self._send_command('setAO_Frequency',param)

    def _frequency5_setter(self,value) -> None:
        param = {'AO Channel': 5, 'Frequency (Hz)':value}
        self._send_command('setAO_Frequency',param)

    def _frequency6_setter(self,value) -> None:
        param = {'AO Channel': 6, 'Frequency (Hz)':value}
        self._send_command('setAO_Frequency',param)

    def _frequency7_setter(self,value) -> None:
        param = {'AO Channel': 7, 'Frequency (Hz)':value}
        self._send_command('setAO_Frequency',param)

    def _frequency8_setter(self,value) -> None:
        param = {'AO Channel': 8, 'Frequency (Hz)':value}
        self._send_command('setAO_Frequency',param)

    def _frequency_getter(self)-> None:
        pass

    def _amplitude1_setter(self,value) -> None:
        param = {'AO Channel': 1, 'Amplitude (V)':value}
        self._send_command('setAO_Amplitude',param)

    def _amplitude2_setter(self,value) -> None:
        param = {'AO Channel': 2, 'Amplitude (V)':value}
        self._send_command('setAO_Amplitude',param)

    def _amplitude3_setter(self,value) -> None:
        param = {'AO Channel': 3, 'Amplitude (V)':value}
        self._send_command('setAO_Amplitude',param)

    def _amplitude4_setter(self,value) -> None:
        param = {'AO Channel': 4, 'Amplitude (V)':value}
        self._send_command('setAO_Amplitude',param)

    def _amplitude5_setter(self,value) -> None:
        param = {'AO Channel': 5, 'Amplitude (V)':value}
        self._send_command('setAO_Amplitude',param)

    def _amplitude6_setter(self,value) -> None:
        param = {'AO Channel': 6, 'Amplitude (V)':value}
        self._send_command('setAO_Amplitude',param)

    def _amplitude7_setter(self,value) -> None:
        param = {'AO Channel': 7, 'Amplitude (V)':value}
        self._send_command('setAO_Amplitude',param)

    def _amplitude8_setter(self,value) -> None:
        param = {'AO Channel': 8, 'Amplitude (V)':value}
        self._send_command('setAO_Amplitude',param)

    def _amplitude_getter(self)-> None:
        pass

    def _DC1_setter(self,value) -> None:
        param = {'AO Channel': 1, 'DC (V)':value}
        self._send_command('setAO_DC',param)

    def _DC2_setter(self,value) -> None:
        param = {'AO Channel': 2, 'DC (V)':value}
        self._send_command('setAO_DC',param)

    def _DC3_setter(self,value) -> None:
        param = {'AO Channel': 3, 'DC (V)':value}
        self._send_command('setAO_DC',param)

    def _DC4_setter(self,value) -> None:
        param = {'AO Channel': 4, 'DC (V)':value}
        self._send_command('setAO_DC',param)

    def _DC5_setter(self,value) -> None:
        param = {'AO Channel': 5, 'DC (V)':value}
        self._send_command('setAO_DC',param)

    def _DC6_setter(self,value) -> None:
        param = {'AO Channel': 6, 'DC (V)':value}
        self._send_command('setAO_DC',param)

    def _DC7_setter(self,value) -> None:
        param = {'AO Channel': 7, 'DC (V)':value}
        self._send_command('setAO_DC',param)

    def _DC8_setter(self,value) -> None:
        param = {'AO Channel': 8, 'DC (V)':value}
        self._send_command('setAO_DC',param)

    def _DC_getter(self)-> None:
        pass

    def _phase1_setter(self,value) -> None:
        param = {'AO Channel': 2, 'Phase (°)':value}
        self._send_command('setAO_Phase',param)

    def _phase2_setter(self,value) -> None:
        param = {'AO Channel': 2, 'Phase (°)':value}
        self._send_command('setAO_Phase',param)

    def _phase3_setter(self,value) -> None:
        param = {'AO Channel': 3, 'Phase (°)':value}
        self._send_command('setAO_Phase',param)

    def _phase4_setter(self,value) -> None:
        param = {'AO Channel': 4, 'Phase (°)':value}
        self._send_command('setAO_Phase',param)

    def _phase5_setter(self,value) -> None:
        param = {'AO Channel': 5, 'Phase (°)':value}
        self._send_command('setAO_Phase',param)

    def _phase6_setter(self,value) -> None:
        param = {'AO Channel': 6, 'Phase (°)':value}
        self._send_command('setAO_Phase',param)

    def _phase7_setter(self,value) -> None:
        param = {'AO Channel': 7, 'Phase (°)':value}
        self._send_command('setAO_Phase',param)

    def _phase8_setter(self,value) -> None:
        param = {'AO Channel': 8, 'Phase (°)':value}
        self._send_command('setAO_Phase',param)

    def _phase_getter(self)-> None:
        pass
 
    def _drain_getter(self):
        key = f"AI{self.drain_channel}.Mean" if self.drain_measurement == 'Mean' else f"AI{self.drain_channel}.Ref{self.drain_ref}.{self.drain_measurement}"

        response = self._send_command('getResults')
        results = response['result']['Results (Dictionary)']
        results_dict = {item['key']: item['value'] for item in results}
        return results_dict.get(key)

    def _drain_setter(self, value) -> None:
        pass



#For "Function", the type of values should be either "Sine", "Triangle", or "Square"
 #   class FunctionParameter(Parameter):
  #  def __init__(self, name: str, **kwargs):
   #     super().__init__(name, 
    #                     validator=Enum('Sine', 'Triangle', 'Square'), 
     #                    **kwargs)




    def set_raw(self, value):
        # Custom logic for setting the function type
        self._value = value

    def get_raw(self):
        return self._value
    

    
if __name__ == '__main__':
    """
    Test the Lockin class
    """
    from qcodes.logger import start_all_logging
    start_all_logging()
    lockin = MCLockin('lockin', 'tcp://localhost:29170')
    lockin.close()