import json
import warnings
from functools import partial
from typing import Any, Optional, Dict, Union
import zmq
from levylabinst.ZMQInstrument import ZMQInstrument
import qcodes.validators as vals

class KrohnHite(ZMQInstrument):
    """
    Class to represent the Krohn-Hite amplifier in the LevyLab Instrument Framework.
    This driver talks to the amplifier via ZMQ.

    Args:
        name: The name used internally by QCoDeS for this driver
        address: The ZMQ server address.
        config: A dictionary of the channel configuration parameters for the amplifier
    """

    def __init__(self, name: str, address: str, config: dict, **kwargs: Any) -> None:
        super().__init__(name=name, address=address, **kwargs)
        self.address = address
        self.config = config

        self.connect_message()
        
        for channel_config in self.config['kh_config_info']:
            channel = channel_config['channel']
            self.add_parameter(f'channel{channel}_gain',
                               label=f'channel{channel} Gain',
                               unit='dB',
                               vals=vals.Enum(1, 10, 100, 1000),
                               get_cmd=self._dump,
                               set_cmd=partial(self._set_gain, channel))

            self.add_parameter(f'channel{channel}_input',
                               label=f'channel{channel} Input Mode',
                               vals=vals.Enum('OFF', 'SE+', 'SE-', 'DIFF'),
                               get_cmd=self._dump,
                               set_cmd=partial(self._set_input, channel))

            self.add_parameter(f'channel{channel}_shunt',
                               label=f'channel{channel} Shunt',
                               unit='Ohms',
                               vals=vals.Enum(0, 50, 500, 5000, 50000, 10000000),
                               get_cmd=self._dump,
                               set_cmd=partial(self._set_shunt, channel))

            self.add_parameter(f'channel{channel}_couple',
                               label=f'channel{channel} Coupling',
                               vals=vals.Enum('AC', 'DC'),
                               get_cmd=self._dump,
                               set_cmd=partial(self._set_coupling, channel))

            self.add_parameter(f'channel{channel}_filter',
                               label=f'channel{channel} Filter',
                               vals=vals.Enum('OFF', 'ON'),
                               get_cmd=self._dump,
                               set_cmd=partial(self._set_filter, channel))
    
    def reload_config(self, new_config):
        """
        Reload the configuration and update channels.
        """
        try:
            existing_channels = {ch['channel'] for ch in self.config['kh_config_info']}
            new_channels = {ch['channel'] for ch in new_config['kh_config_info']}

            for channel in existing_channels - new_channels:
                del self.parameters[f'channel{channel}_gain']
                del self.parameters[f'channel{channel}_input']
                del self.parameters[f'channel{channel}_shunt']
                del self.parameters[f'channel{channel}_couple']
                del self.parameters[f'channel{channel}_filter']

            for channel in new_channels & existing_channels:
                del self.parameters[f'channel{channel}_gain']
                del self.parameters[f'channel{channel}_input']
                del self.parameters[f'channel{channel}_shunt']
                del self.parameters[f'channel{channel}_couple']
                del self.parameters[f'channel{channel}_filter']

            self.config['kh_config_info'] = new_config['kh_config_info']

            # Reinitialize parameters
            for channel_config in self.config['kh_config_info']:
                channel = channel_config['channel']
                self.add_parameter(f'channel{channel}_gain',
                                   label=f'channel{channel} Gain',
                                   unit='dB',
                                   vals=vals.Enum(1, 10, 100, 1000),
                                   get_cmd=self._dump,
                                   set_cmd=partial(self._set_gain, channel))

                self.add_parameter(f'channel{channel}_input',
                                   label=f'channel{channel} Input Mode',
                                   vals=vals.Enum('OFF', 'SE+', 'SE-', 'DIFF'),
                                   get_cmd=self._dump,
                                   set_cmd=partial(self._set_input, channel))

                self.add_parameter(f'channel{channel}_shunt',
                                   label=f'channel{channel} Shunt',
                                   unit='Ohms',
                                   vals=vals.Enum(0, 50, 500, 5000, 50000, 10000000),
                                   get_cmd=self._dump,
                                   set_cmd=partial(self._set_shunt, channel))

                self.add_parameter(f'channel{channel}_couple',
                                   label=f'channel{channel} Coupling',
                                   vals=vals.Enum('AC', 'DC'),
                                   get_cmd=self._dump,
                                   set_cmd=partial(self._set_coupling, channel))

                self.add_parameter(f'channel{channel}_filter',
                                   label=f'channel{channel} Filter',
                                   vals=vals.Enum('OFF', 'ON'),
                                   get_cmd=self._dump,
                                   set_cmd=partial(self._set_filter, channel))

            print("Config reloaded successfully.")
        except Exception as e:
            print(f"Failed to reload configuration: {e}")

    def set_all_channels(self, channels_config: list[dict]) -> dict:
        """
        Set the configuration for all channels.
        channels_config is a list of dictionaries where each dictionary has keys:
        'channel', 'gain', 'input', 'shunt', 'couple', 'filter'.
        """

        for channel_config in channels_config:
            channel = channel_config['channel']
            gain = channel_config['gain']
            input_mode = channel_config['input']
            shunt = channel_config['shunt']
            couple = channel_config['couple']
            filter = channel_config['filter']
            
        # Validate and set all channels
        return self._send_command('setAllChannels', channels_config)

    def get_all_channels(self) -> list[dict]:
        """
        Get the configuration for all channels.
        Returns a list of dictionaries where each dictionary has keys:
        'channel', 'gain', 'input', 'shunt', 'couple', 'filter'.
        """
        response = self._send_command('getAllChannels')
        return response.get('result', [])
    
    def get_idn(self) -> dict[str, Optional[str]]:
        idn_info = super().get_idn()  # Reuse the parent method
        idn_info["model"] = "Krohn-Hite"  # Override the model field
        return idn_info
    
    def connect_message(self) -> None:
        """
        Print a connection message for the amplifier.
        """
        print(f"Connected to Krohn-Hite amplifier at address {self.address}.")
        print(f"Configuration file loaded: {self.config}")

    # Placeholder functions for setting commands to the instrument
    def _dump(self):
        pass

    def _set_gain(self, channel: int, value: float) -> None:
        param = {'channel': channel, 'gain': value}
        self._send_command('setChannelGain', param)

    def _set_input(self, channel: int, value: str) -> None:
        param = {'channel': channel, 'input': value}
        self._send_command('setChannelInput', param)

    def _set_shunt(self, channel: int, value: float) -> None:
        param = {'channel': channel, 'shunt': value}
        self._send_command('setChannelShunt', param)

    def _set_coupling(self, channel: int, value: str) -> None:
        param = {'channel': channel, 'couple': value}
        self._send_command('setChannelCoupling', param)

    def _set_filter(self, channel: int, value: str) -> None:
        param = {'channel': channel, 'filter': value}
        self._send_command('setChannelFilter', param)
