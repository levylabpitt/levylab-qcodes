"""ZMQ Communication driver based on pyzmq."""
import time
import json
import logging
import warnings
import zmq
from importlib.resources import as_file, files
from typing import TYPE_CHECKING, Any, Union, Sequence, Optional
from weakref import finalize
from functools import partial
import qcodes.validators as vals
from qcodes.logger import get_instrument_logger
from qcodes.utils import DelayedKeyboardInterrupt

from qcodes.instrument import Instrument
from qcodes.instrument.base import InstrumentBase

if TYPE_CHECKING:
    from collections.abc import Sequence

ZMQ_LOGGER = '.'.join((InstrumentBase.__module__, 'com', 'visa'))

log = logging.getLogger(__name__)


def _close_zmq_socket(socket: zmq.Socket, name: str) -> None:
    try:
        socket.close()
        log.info("Closed ZMQ socket for %s", name)
    except Exception as e:
        log.error("Error closing ZMQ socket for %s: %s", name, str(e))


class ZMQInstrument(Instrument):
    """
    Base class for all instruments using ZMQ communication.
    Used for communication with Levylab Instrument Framework.

    Args:
        name: What the instrument is called locally.
        address: The ZMQ resource name to use to connect.
        timeout: Seconds to allow for responses. Default 5.
        metadata: Additional static metadata to add to this
            instrument's JSON snapshot.
    """
# TODO: Give an option to change the data_source in the constructor
    def __init__(
        self,
        name: str,
        address: str,
        data_source: str = None,
        timeout: float = 5,
        metadata: dict[str, Any] = None,
        **kwargs: Any,
    ):
        super().__init__(name, **kwargs)
        self.zmq_log = get_instrument_logger(self, ZMQ_LOGGER)

        self.add_parameter(
            "commands",
            get_cmd=partial(self.help, "")
        )

        self.add_parameter(
            "zmq_timeout",
            get_cmd=self._get_zmq_timeout,
            set_cmd=self._set_zmq_timeout,
            unit="s",
            vals=vals.MultiType(vals.Numbers(min_value=0), vals.Enum(None)),
        )

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(address)
        finalize(self, _close_zmq_socket, self.socket, str(self.name))

        self._address = address
        self._timeout = timeout
        self.socket.setsockopt(zmq.RCVTIMEO, int(timeout * 1000))
        self.socket.setsockopt(zmq.SNDTIMEO, int(timeout * 1000))

    """def get_idn(self) -> dict[str, Optional[str]]:
        
        # JSON request of IDN should return this information from the IF. 
        # It'd be better to handle this in the child instrument level: 
        # So that IDN is handled for each instrument separately.
        # Or maybe not, since the IDN is a standard command.
        
        return {
            "vendor": "Quantum Design PPMS",
            "model": "Simulation",
            "serial": None,
            "firmware": None,
        }"""
    
    def get_idn(self) -> dict[str, Optional[str]]:
        """
        Returns identification information for the instrument.
        Specific instruments can override the "model" or other fields.
        """
        return {
            "vendor": "LevyLab",
            "model": "Generic ZMQ Instrument",  # Default model
            "serial": None,
            "firmware": "v1.0.0",
        }

    def help(self, method: str = None) -> Sequence[str]:
        if method:
            response = self._send_command("HELP", {"method": method})
            if response and "result" in response:
                return response["result"]
            return None
        else:
            response = self._send_command("HELP")
            if response and "result" in response:
                return response["result"][5:] # Skip the first 4 commands
            return None

    def _set_zmq_timeout(self, timeout: Union[float, None]) -> None:
        if timeout is None:
            self.socket.setsockopt(zmq.RCVTIMEO, -1)
            self.socket.setsockopt(zmq.SNDTIMEO, -1)
        else:
            self.socket.setsockopt(zmq.RCVTIMEO, int(timeout * 1000))
            self.socket.setsockopt(zmq.SNDTIMEO, int(timeout * 1000))
        self._timeout = timeout

    def _get_zmq_timeout(self) -> Union[float, None]:
        timeout = self.socket.getsockopt(zmq.RCVTIMEO)
        if timeout == -1:
            return None
        else:
            return timeout / 1000.0

    def close(self) -> None:
        """Disconnect and irreversibly tear down the instrument."""
        print('Closing server connection...')  
        try:   
            if getattr(self, 'socket', None):
                self.socket.close()
                self.context.term()
            super().close()
        except:
            self.log.info('Could not close connection to server, perhaps the '
                          'server is down?')
    
    def _send_command(self, cmd: str, params: dict = {}, *args: Any) -> str:
        command: dict = {"jsonrpc": "2.0", 
            "method": cmd,
            "params": params,
            "id": str(int(time.time()))} 
        cmd: str = json.dumps(command)
        response = self.ask_raw(cmd)
        return response

    def write_raw(self, cmd: str) -> None:
        """
        Low-level interface to send a command to the ZMQ socket.

        Args:
            cmd: The command to send to the instrument.
        """
        with DelayedKeyboardInterrupt():
            self.zmq_log.debug(f"Writing: {cmd}")
            self.socket.send_string(cmd)

    def ask_raw(self, cmd: str) -> str:
        """
        Low-level interface to send a command to the ZMQ socket and receive a response.

        Args:
            cmd: The command to send to the instrument.

        Returns:
            str: The instrument's response.
        """
        with DelayedKeyboardInterrupt():
            self.zmq_log.debug(f"Querying: {cmd}")
            self.socket.send_string(cmd)
            response = self.socket.recv_string()
            self.zmq_log.debug(f"Response: {response}")
            response: dict = json.loads(response)
        return response