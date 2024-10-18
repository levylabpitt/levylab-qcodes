#%% Imports
import sys
import os
from config_watcher import get_latest_config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from levylabinst.KrohnHite import KrohnHite
kh_address = 'tcp://localhost:29160'

# %% Database handling
latest_config_data = get_latest_config()
kh_config_info = latest_config_data.get('kh_config_info', [])
# TODO: Fix error with the config dictionary

kh = KrohnHite('kh', kh_address, config={'kh_config_info': kh_config_info})

#%%
kh._send_command("HELP")
# TODO: Make functions for each API returned from the above method.

# %%
kh.set_all_channels(kh_config_info)

# %%
kh.get_all_channels()

# %%
kh.set_channel(2)

# %%
kh.get_channel(2)

# %%
print("Sending configuration:", kh_config_info)

# %%
print("KH Config Info being sent:", kh_config_info)

# %%
