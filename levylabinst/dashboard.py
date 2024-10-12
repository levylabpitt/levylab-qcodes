import tkinter as tk
from tkinter import font as tkFont
from tkinter import simpledialog, messagebox

class Dashboard:
    def __init__(self, lockin_config_info, wirebonding_info, kh_config_info, experiment_note_info):
        self.lockin_config_info = lockin_config_info
        self.kh_config_info = kh_config_info
        self.wirebonding_info = wirebonding_info
        self.experiment_note_info = experiment_note_info

    def launch(self):
        """
        Launches a dashboard where the user can view existing channels, 
        wirw-bonding info,
        krohn-hite info,
        and view experiment description.
        """
        
        # Create the dashboard window
        dashboard = tk.Tk()
        dashboard.title("Experiment Dashboard")

        # Function to update the dashboard with the current channels and additional info
        def update_dashboard():

            row = 0
            bold_italic_font = tkFont.Font(family="Helvetica", size=10, weight="bold", slant="italic")
            #Clear all existing widgets from the window before refreshing
            for widget in dashboard.grid_slaves():
                widget.grid_forget()

            # Display MCLockin configuration if available
            if self.lockin_config_info:
                tk.Label(dashboard, text="Lockin Channels:", font=bold_italic_font).grid(row=0, column=0, columnspan=2)

                row += 1
                for label, lead_number in self.lockin_config_info.items():
                    tk.Label(dashboard, text=f"Channel {label}:").grid(row=row, column=0)
                    tk.Label(dashboard, text=f"Lead Number {lead_number}").grid(row=row, column=1)
                    row += 1
            else:
                print("No lockin_config_info in config.")

            # Display Krohn-Hite configuration if available
            if self.kh_config_info:
                tk.Label(dashboard, text="Krohn-Hite Configurations:", font=bold_italic_font).grid(row=row, column=0, columnspan=2)

                row += 1
                for kh_channel in self.kh_config_info:
                    channel = kh_channel['channel']
                    gain = kh_channel['gain']
                    input_type = kh_channel['input']
                    shunt = kh_channel['shunt']
                    couple = kh_channel['couple']
                    filter_status = kh_channel['filter']
                    tk.Label(dashboard, text=f"Channel {channel}:").grid(row=row, column=0)
                    tk.Label(dashboard, text=f"Gain: {gain}, Input: {input_type}, Shunt: {shunt}, Couple: {couple}, Filter: {filter_status}").grid(row=row, column=1)
                    row += 1
            else:
                print("No kh_config_info in config.")
            
            # Display wirebonding details
            if self.wirebonding_info:
                tk.Label(dashboard, text="Wirebonding Description:", font=bold_italic_font).grid(row=row, column=0, columnspan=2)

                row += 1
                tk.Label(dashboard, text="WireBonding Info:").grid(row=row, column=0, sticky="w")
                tk.Label(dashboard, text=self.wirebonding_info).grid(row=row, column=1, sticky="w")
                row += 1

            # Display experiment notes
            if self.experiment_note_info:
                tk.Label(dashboard, text="Experiment Description:", font=bold_italic_font).grid(row=row, column=0, columnspan=2)

                row += 1
                tk.Label(dashboard, text="Experiment Note:").grid(row=row, column=0, sticky="w")
                tk.Label(dashboard, text=self.experiment_note_info).grid(row=row, column=1, sticky="w")
                row += 1

            # OK button to close the dashboard
            ok_button = tk.Button(dashboard, text="OK", command=dashboard.destroy)
            ok_button.grid(row=row + 1, column=0, columnspan=2)

        # Initially update the dashboard when the window is created
        update_dashboard()

        # Start the dashboard main loop
        dashboard.mainloop()