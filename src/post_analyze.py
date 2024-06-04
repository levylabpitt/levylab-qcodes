import qcodes as qc
from qcodes.dataset.measurements import Measurement
from qcodes.dataset.sqlite.database import initialise_database, connect
from qcodes.dataset.experiment_container import load_by_id
import matplotlib.pyplot as plt
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

# Path to your saved database file
database_path = 'D:\qcodesdb\experiment.db'

# Initialize the database connection
qc.config["core"]["db_location"] = database_path
initialise_database()
conn = connect(database_path)

# Load data from a specific run ID
run_id = 1
data_set = load_by_id(run_id)

plot_dataset(data_set)
# Get the data as a pandas DataFrame
# data = data_set.to_pandas_dataframe()

# Display the data
# print(data.head())

# # Plot the data
# plt.plot(data['lockin_gate'], data['lockin_drain'])
# plt.xlabel('Parameter Name')
# plt.ylabel('Measured Value')
# plt.title('Measurement Data')
# plt.show()
