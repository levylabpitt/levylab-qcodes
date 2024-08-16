# Explanation for main.py file 
The `main.py` file is a sample python file where we have shown how to call "PPMS" and "Lock-in" instruments and perform a demo experiment using the package "Qcodes". In the following sections, the different parts of the code will be explained.

### Importing the Modules to perform the experiment
At first, we are importing the necessary modules for performing the experiment:
````python
#%% Imports
import sys
import json
import qcodes as qc
import os
import numpy as np
import qcodes as qc
## Logging
from qcodes.logger import start_all_logging
## Multidimensional scanning module
from qcodes.dataset import (
    LinSweep,
    Measurement,
    dond,
    experiments,
    initialise_or_create_database_at,
    load_by_run_spec,
    load_or_create_experiment,
    plot_dataset,
)
## Using interactive widget
from qcodes.interactive_widget import experiments_widget

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
start_all_logging()
````
### Including the instruments and adding the parameters
As next step, we are calling the two main instrument driver files- `PPMS.py` and `Lock-in.py` from the `levylabinst` package amd then, adding the necessary parameters along with instrument files:
````python 
#%% Create the instrument objects
from levylabinst import PPMSSim, MCLockin
ppms_address = 'tcp://localhost:29270'
lockin_address = 'tcp://localhost:29170'
ppms = PPMSSim('ppms', ppms_address)
lockin = MCLockin('lockin', lockin_address)
# ppms.field([1,5])
# print(ppms._send_command('Get Magnet'))
````
### Making the station and adding the instruments
Then, we instantiate a station and add the instruments in that station:

````python
# %% Station
station = qc.Station()
station.add_component(ppms)
station.add_component(lockin)
````
### Creating a database 
Now, to save the experimental data, we set up a database:
````python
# %% Database
initialise_or_create_database_at(r'C:\qcodesdb\experiment.db')
qc.config.core.db_location
````
### Creating the experiment
After creating the database, an `experiment` objected is loaded or created and this object will now act as a manager for the data acquired during the experiment:
````python 
# %% Experiment
test_exp = load_or_create_experiment('test_exp', sample_name='SimWaveguide')
````
### Measurement process
We use the `measurement` object to obtain the data from the instruments. This object uses `experiment` and `station` objects to handle the data and control the instruments respectively. After initiating with this `measurement` object, the parameteres which will be measured are registered.

````python
# %% Measurement
meas = Measurement(exp=test_exp, station=station, name='TestMeasurement')
meas.register_parameter(ppms.temperature)
meas.register_parameter(ppms.field)
meas.register_parameter(lockin.gate)
meas.register_parameter(lockin.drain, setpoints=(lockin.gate,)) # dependent parameter
````
### Creating the example measurement loop
In this step, we create a loop inside the context manager where we control the instruments, acquire the data, and store the results. In the following code-part, the `meas.run` method returns a context manager to control data acquisition and storage. Entering the context provides a `DataSaver` object, which we will store as the `datasaver` variable.
````python
# %% Example Measurement Loop
import time
with meas.run() as datasaver:
    for temp in np.linspace(270, 275, 2):
        ppms.temperature([temp, 50])
        for field in np.linspace(0, 0.1, 2):
            ppms.field([field, 2])
            lockin.gate(0)
            time.sleep(1)
            for gate in np.linspace(0, 0.1, 500):
                lockin.gate(gate)
                get_drain = lockin.drain()
                datasaver.add_result((ppms.temperature, temp),
                                     (ppms.field, field),
                                     (lockin.gate, gate),
                                     (lockin.drain, get_drain))
````
### Working with dataset
In QCoDeS, all measured results are generally packaged and stored in the database as a `DataSet` object. Using the `experiment` function, we intialize the database and print the `experiments` and `datasets` contained inside. Then, using the `data_sets` method we can print a list of these `datasets`, the parameters recorded, and the type of data obtained for each parameter under the `experiment`.

````python
# %% Explore Experiments and Datasets
experiments()
test_exp.data_sets()
````
### Loading and Plotting the datasets
In order to plot or analyze data, we will need to retrieve the `datasets`. In QCoDeS, `datasets` can be obtained using simple criteria via the  `load_by_run_spec` function.  For this example we will load our datasets by calling their name and database id number. Also, to visualize the dataset as a plotting, we use `plot_dataset` function.

````python
# %% Load and Plot Dataset
dataset = load_by_run_spec(experiment_name='test_exp', captured_run_id=1)
plot_dataset(dataset)
````
### Interactive_Widget
Using `Interactive_Widget`, we get an overview of the experiment performed. In this overview parameter details, snapshots, plots, etc. will be provided and the user will be able to analyze the experimental results more thoroughly:
````python
# %% Interactive Widget
experiments_widget(sort_by='run_id')
````
# Heirarchy of the Qcodes
Here we will summarize/understand the coding-sequences mentioned in the `main.py` file. At first, we will list the steps in the following:
1. In the first step, we import the required modules. Alongside we create the station and add the instruments in this station. Also, we create a database where the experimental data will be saved later.
2. As the second step, we load/create the experiment.
3. For the third step, we register parameters for measurement and create measurement loop to conduct the experiment.
4. Finally, we explore the dataset by plotting the results and using the `interactive_widget`.


So, we can use the above mentioned points as the building blocks to make the heirarchy of the Qcodes operation. The Heirarchy is shown here following:

![Heirarchy](\docs\Qcodes Heirarchy V1.png) 






