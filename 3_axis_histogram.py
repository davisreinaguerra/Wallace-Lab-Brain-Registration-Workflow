import tkinter as tk
import easygui
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import matplotlib.pyplot as plt
from brainrender import Scene

# Global Variables ______________________________________________________
background_color_all = "#DBE4E5"
name = "Title"  # default
data_um = None
bounding_box = None
title = None
x_color = "#58229D"
y_color = "#BB8651"
z_color = "#51AEBB"
plot_fontsize = 12
AP_title = "A <----------------------------------------> P"
DV_title = "D <----------------------------------------> V"
LR_title = "L <--------------------M-------------------> R"

scene = Scene(atlas_name="allen_mouse_25um")

# Command Functions __________________________________________________
def clear_and_refresh():
    working_xlim_X = axs[0].get_xlim()
    working_xlim_Y = axs[1].get_xlim()
    working_xlim_Z = axs[2].get_xlim()
    axs[0].clear()
    axs[1].clear()
    axs[2].clear()
    axs[0].set_title(AP_title, fontsize=plot_fontsize)
    axs[1].set_title(DV_title, fontsize=plot_fontsize)
    axs[2].set_title(LR_title, fontsize=plot_fontsize)
    axs[0].set_xlim(working_xlim_X)
    axs[1].set_xlim(working_xlim_Y)
    axs[2].set_xlim(working_xlim_Z)
    axs[0].set_xlabel("micrometers", fontsize=16)
    axs[1].set_xlabel("micrometers", fontsize=16)
    axs[2].set_xlabel("micrometers", fontsize=16)
    axs[0].set_ylabel("frequency", fontsize=plot_fontsize)
    axs[2].axvline(x=5700, label="midline")

def change_title_to(value):
    fig.suptitle(value, fontsize=24, y=.99)
    canvas.draw()

def change_bin_size(value):
    clear_and_refresh()

    axs[0].hist(data_um["Allen CCFv3 X mm"], bins=value, color=x_color)
    axs[1].hist(data_um["Allen CCFv3 Y mm"], bins=value, color=y_color)
    axs[2].hist(data_um["Allen CCFv3 Z mm"], bins=value, color=z_color)
    canvas.draw()

def configure_xlimits_by_structure(value):
    global bounding_box
    cp = scene.add_brain_region(value)
    bounding_box = cp.mesh.bounds()

    axs[0].set_xlim(bounding_box[0], bounding_box[1])
    axs[1].set_xlim(bounding_box[2], bounding_box[3])
    axs[2].set_xlim(bounding_box[4], bounding_box[5])
    canvas.draw()

def update_name(selection):
    global name
    name = selection

def load_file():
    clear_and_refresh()
    global data_um
    file_path = easygui.fileopenbox(filetypes=["*.csv"])
    data_mm = pd.read_csv(file_path)
    data_um = data_mm * 1000

    axs[0].hist(data_um["Allen CCFv3 X mm"], bins="auto", color=x_color)
    axs[1].hist(data_um["Allen CCFv3 Y mm"], bins="auto", color=y_color)
    axs[2].hist(data_um["Allen CCFv3 Z mm"], bins="auto", color=z_color)
    canvas.draw()

def run_command():
    selected_name = name
    value = command_value_entry.get().strip()
    if selected_name == "Title":
        change_title_to(value)
    elif selected_name == "n_Bins":
        value_int = int(value)
        change_bin_size(value_int)
    elif selected_name == "Structure":
        configure_xlimits_by_structure(value)
    else:
        print("error: no entry")

# Initiate ____________________________________________________________
frame = tk.Tk()
frame.title("Anatomy Histogram Creator")
frame.configure(bg=background_color_all)

# Set fixed width and adjustable height for the GUI
frame.geometry("1500x600")  # Width is fixed at 1000px, height adjustable

# Create Hist _________________________________________________________
fig, axs = plt.subplots(1, 3, figsize=(15, 4), sharey=True, facecolor=background_color_all)  # Decrease the height
fig.suptitle("Title", fontsize=24, y=.99)

axs[0].hist([], bins="auto", color=x_color)
axs[1].hist([], bins="auto", color=y_color)
axs[2].hist([], bins="auto", color=z_color)
axs[0].set_title(AP_title, fontsize=plot_fontsize)
axs[1].set_title(DV_title, fontsize=plot_fontsize)
axs[2].set_title(LR_title, fontsize=plot_fontsize)
axs[0].set_xlim(0, 13000)
axs[1].set_xlim(0, 8000)
axs[2].set_xlim(0, 11400)
axs[0].set_xlabel("micrometers", fontsize=plot_fontsize)
axs[1].set_xlabel("micrometers", fontsize=plot_fontsize)
axs[2].set_xlabel("micrometers", fontsize=plot_fontsize)
axs[0].set_ylabel("frequency", fontsize=plot_fontsize)
axs[2].axvline(x=5700, label="midline")

canvas = FigureCanvasTkAgg(fig, master=frame)
canvas.draw()
canvas.get_tk_widget().grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")

"""
Widgets
"""
# Load Button ________________________________________________
load_button = tk.Button(
    frame,
    text="Load File",
    font=("Arial", 16),
    command=load_file,
    relief=tk.RAISED,  # Keep raised
    borderwidth=5,
    height=1
)
load_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

# Command Name OptionMenu______________________________________________
options = ["Title", "n_Bins", "Structure"]
selected_option = tk.StringVar(frame)
selected_option.set(options[0])

command_name_optionmenu = tk.OptionMenu(
    frame,
    selected_option,
    *options,
    command=update_name,
)
command_name_optionmenu.config(width=15, relief="flat", bg="WHITE", font=("Arial", 16))  # Adjust width and font size
command_name_optionmenu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

# Command Value ________________________________________________________
command_value_entry = tk.Entry(
    frame,
    width=20,
    relief=tk.FLAT,  # Flat relief
    borderwidth=5,
    bg="WHITE",
    font=("Arial", 16)
)
command_value_entry.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

# Run Command Button ________________________________________________
command_button = tk.Button(
    frame,
    text="Run Command",
    font=("Arial", 16),
    command=run_command,
    relief=tk.RAISED,  # Keep raised
    borderwidth=5,
    height=1
)
command_button.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

# Adjust column weights so that the widgets and canvas expand properly
frame.grid_columnconfigure(0, weight=1)
frame.grid_columnconfigure(1, weight=1)
frame.grid_columnconfigure(2, weight=1)
frame.grid_columnconfigure(3, weight=1)

# Ensure canvas is expandable
frame.grid_rowconfigure(1, weight=1)

plt.close()
frame.mainloop()
