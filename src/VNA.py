#%%Importing modules
import qcodes as qc

#%%Calling modules
from qcodes.instrument_drivers.rohde_schwarz import (
    RohdeSchwarzZNB8,
    RohdeSchwarzZNBChannel,
)


from qcodes.dataset import (
    Measurement,
    initialise_database,
    load_or_create_experiment,
    plot_by_id,
)

#%% DataBase
initialise_database()
load_or_create_experiment(experiment_name="test_with_znb8", sample_name="no sample")

#%%Create the instrument
vna = RohdeSchwarzZNB8("VNA", "TCPIP0::192.168.15.104::inst0::INSTR")

#%%including the station in station
station = qc.Station(vna)

#%%Turning on the power in its default
vna.channels.power(-50)
vna.rf_on()

#%%Autoscaling the power values
vna.channels.autoscale()

#%%Measuring S11 from 100 KHz to 1 MHz in 100 steps with a power of -30 dB
vna.channels.S11.start(100e3)
vna.channels.S11.stop(6e6)
vna.channels.S11.npts(100)
vna.channels.S11.power(-30) #for the power

#%%Measuring a frequency trace
vna.rf_on()
meas = Measurement()
meas.register_parameter(vna.channels.S11.trace)
with meas.run() as datasaver:
    get_v = vna.channels.S11.trace.get()
    datasaver.add_result((vna.channels.S11.trace, get_v))

#%%Plotting the experimental result
ax, cbax = plot_by_id(datasaver.run_id)


