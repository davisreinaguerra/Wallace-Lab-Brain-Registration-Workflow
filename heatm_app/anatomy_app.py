# Custom Libraries
from twoD_heatmap_functions import *
#from threeD_histogram_functions import *
# GUI
import tkinter as tk
import easygui
# Figure Control
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.colors import ListedColormap
# Misc
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde
from scipy.ndimage import gaussian_filter
# Brainrender
from brainrender import Scene

"""
Global Variables ____________________________________________________________________________________________________"""

scene = Scene(atlas_name="allen_mouse_25um")
global_font = "Consolas"
global_fontsize = 12
title_fontsize = 20
background_color = "#F0F0F0"
heatmap_name = "Title"  # default
threeaxis_name = "Title"  # default
data_um = None
mesh_verts = None
bounding_box = None
title = None
x_color = "#58229D"
y_color = "#BB8651"
z_color = "#51AEBB"
RC_title = "R <---------------> C"
DV_title = "D <---------------> V"
LR_title = "L <-------M-------> R"
rc_data = None
dv_data = None
lr_data = None
rc_limits = None
dv_limits = None
lr_limits = None
n_bins = None
bin_edges = None
rc_shadow = None
dv_shadow = None
lr_shadow = None
previous_lines = []


"""
Global Functions ____________________________________________________________________________________________________"""

def add_message(message):
    readout_area.config(state=tk.NORMAL)
    readout_area.insert(tk.END, message + "\n")
    readout_area.see(tk.END)
    readout_area.config(state=tk.DISABLED)

def create_transparent_bottomed_cmap(predefined_cmap_name):
    default_cmap = plt.get_cmap(predefined_cmap_name)
    ncolors = default_cmap.N

    # Create a gradient from transparent to the colors of the original colormap
    transparent_colors = np.zeros((ncolors, 4))
    transparent_colors[:, 0:3] = default_cmap(np.linspace(0, 1, ncolors))[:, 0:3]  # Get RGB values
    transparent_colors[:, 3] = np.linspace(0, 1, ncolors)  # Alpha from 0 (transparent) to 1 (opaque)

    # Create the final colormap
    return ListedColormap(transparent_colors)

"""
Callback Functions __________________________________________________________________________________________________"""

def load_data():
    global rc_data
    global dv_data
    global lr_data
    global rc_limits
    global dv_limits
    global lr_limits
    global data_um
    global mesh_verts
    global rc_shadow
    global dv_shadow
    global lr_shadow

    file_path = easygui.fileopenbox()
    data_mm = pd.read_csv(file_path)
    data_um = data_mm * 1000

    # Raw data for each axis
    rc_data = data_um["Allen CCFv3 X mm"]
    dv_data = data_um["Allen CCFv3 Y mm"]
    lr_data = data_um["Allen CCFv3 Z mm"]

    structure_ids = easygui.enterbox("Name of Structures separated by Comma:", "Input")
    structure_ids_array = structure_ids.split(",")
    add_message(f"Structure ID's: {structure_ids_array}")


    mesh_verts = []

    for entry in structure_ids_array:
        structure = scene.add_brain_region(entry)
        new_mesh_verts = structure.mesh.vertices
        if new_mesh_verts is not None:
            mesh_verts.append(new_mesh_verts)
        else:
            add_message(f"No vertices found for structure: {entry}")

    if len(mesh_verts) == 0:
        add_message("No mesh vertices found. Please check the structure IDs.")
        return

    mesh_verts = np.concatenate(mesh_verts, axis=0)
    rc_shadow = mesh_verts[:, 0]
    dv_shadow = mesh_verts[:, 1]
    lr_shadow = mesh_verts[:, 2]

    x_min = np.min(mesh_verts[:, 0])
    x_max = np.max(mesh_verts[:, 0])
    y_min = np.min(mesh_verts[:, 1])
    y_max = np.max(mesh_verts[:, 1])
    z_min = np.min(mesh_verts[:, 2])
    z_max = np.max(mesh_verts[:, 2])

    # Create the bounding box array
    bounding_box = [x_min, x_max, y_min, y_max, z_min, z_max]
    print(bounding_box)

    # Define the limits
    rc_limits = [bounding_box[0], bounding_box[1]]
    dv_limits = [bounding_box[2], bounding_box[3]]
    lr_limits = [bounding_box[4], bounding_box[5]]

    

    print(rc_limits)
    print(dv_limits)
    print(lr_limits)

    # Shadowed HeatMap _________________________________________________________________________________________________
    n_cells = plot_shadowed_heatmap(
        ax_lrdv,
        ax_rcdv,
        rc_data,
        lr_data,
        dv_data,
        rc_shadow,
        lr_shadow,
        dv_shadow,
        rc_limits,
        lr_limits,
        dv_limits,
        bin_edges = None,
        binned_lr_data = None,
        binned_dv_data = None,
        binned_lr_shadow = None,
        binned_dv_shadow = None
    )
    heatmap_canvas.draw()

    # Threeaxis ________________________________________________________________________________________________________
    axs[0].hist(data_um["Allen CCFv3 X mm"], bins="auto", color=x_color)
    axs[1].hist(data_um["Allen CCFv3 Y mm"], bins="auto", color=y_color)
    axs[2].hist(data_um["Allen CCFv3 Z mm"], bins="auto", color=z_color)
    axs[0].set_xlim(rc_limits[0], rc_limits[1])
    axs[1].set_xlim(dv_limits[0], dv_limits[1])
    axs[2].set_xlim(lr_limits[0], lr_limits[1])

    threeaxis_canvas.draw()
    add_message("Data Loaded")

def on_scale(val):
    global bin_edges
    global rc_data
    global dv_data
    global lr_data
    global rc_limits
    global dv_limits
    global lr_limits
    global data_um
    global mesh_verts
    global rc_shadow
    global dv_shadow
    global lr_shadow
    global previous_lines

    # get rid of old axvlines
    for line in previous_lines:
        line.remove()
    previous_lines.clear()

    current_bin = int(val)
    current_bin_edges = [bin_edges[current_bin], bin_edges[current_bin+1]]
    binned_data_um = data_um[
        (data_um['Allen CCFv3 X mm'] >= current_bin_edges[0]) &
        (data_um['Allen CCFv3 X mm'] < current_bin_edges[1])
    ]
    binned_shadow = mesh_verts[
        (mesh_verts[:, 0] >= bin_edges[current_bin]) & 
        (mesh_verts[:, 0] < bin_edges[current_bin + 1])
    ]

    binned_dv_data = binned_data_um["Allen CCFv3 Y mm"]
    binned_lr_data = binned_data_um["Allen CCFv3 Z mm"]

    binned_dv_shadow = binned_shadow[:, 1]
    binned_lr_shadow = binned_shadow[:, 2]


    n_cells = plot_shadowed_heatmap(
        ax_lrdv,
        ax_rcdv,
        rc_data,
        lr_data,
        dv_data,
        rc_shadow,
        lr_shadow,
        dv_shadow,
        rc_limits,
        lr_limits,
        dv_limits,
        bin_edges=current_bin_edges,
        binned_lr_data=binned_lr_data,
        binned_dv_data=binned_dv_data,
        binned_lr_shadow=binned_lr_shadow,
        binned_dv_shadow=binned_dv_shadow
    )

    rostral = ax_rcdv.axvline(x=current_bin_edges[0], color="black")
    caudal = ax_rcdv.axvline(x=current_bin_edges[1], color="black")
    previous_lines.extend([rostral, caudal])

    heatmap_canvas.draw()

    add_message(f"Showing heatmap of rc range {current_bin_edges[0]}mm to {current_bin_edges[1]}mm")
    add_message(f"Based on a total of {n_cells} cells")

def update_name_heatmap(selection):
    global heatmap_name
    heatmap_name = selection

def update_name_threeaxis(selection):
    global threeaxis_name
    threeaxis_name = selection

def run_heatmap_command():
    global rc_limits
    global n_bins
    global bin_edges

    selected_name = heatmap_name
    value = command_value_heatmap.get().strip()
    if selected_name == "Title":
        heatmap_fig.suptitle(value, fontsize=title_fontsize, y=.99)
        heatmap_canvas.draw()
    elif selected_name == "Slice":
        n_bins = int(value)
        bin_edges = np.round(np.linspace(rc_limits[0], rc_limits[1], n_bins + 1)).astype(int)
        slice_slider.config(from_=0, to_=n_bins-1, showvalue=False)
        add_message("Sliced!")
    else:
        print("error: no entry")

def run_threeaxis_command():
    selected_name = threeaxis_name
    value = command_value_threeaxis.get().strip()
    if selected_name == "Title":
        threeaxis_fig.suptitle(value, fontsize=title_fontsize, y=.99)
        threeaxis_canvas.draw()
    elif selected_name == "n_bins":
        value_int = int(value)
        change_bin_size(value_int)
    else:
        print("error: no entry")


def save_heatmap():
    print("Under construction save heatmap")
    """for i in range(len(bin_edges) - 1):
        binned_data_um = data_um[(data_um['Allen CCFv3 X mm'] >= bin_edges[i]) & (data_um['Allen CCFv3 X mm'] < bin_edges[i + 1])]
        binned_shadow = mesh_verts[(mesh_verts[:, 0] >= bin_edges[i]) & (mesh_verts[:, 0] < bin_edges[i + 1])]

        binned_dv_data = binned_data_um["Allen CCFv3 Y mm"]
        binned_lr_data = binned_data_um["Allen CCFv3 Z mm"]

        binned_dv_shadow = binned_shadow[:, 1]
        binned_lr_shadow = binned_shadow[:, 2]

        # Pass the current bin edges to the plot function
        plot_shadowed_heatmap_and_histogram(
            binned_lr_data,
            binned_dv_data,
            binned_lr_shadow,
            binned_dv_shadow,
            lr_limits,
            dv_limits,
            save_dir,
            bin_edges=[bin_edges[i], bin_edges[i + 1]]
        )"""
        #save_dir = easygui.diropenbox(title="Select Directory to Save Figures")
        # If bin edges is None, save the collapsed
        # If bin edges is not none, run the above for loop to save the sliced files


def save_threeaxis():
    print("Under construction save threeaxis")

"""

App Creation ________________________________________________________________________________________________________"""

root = tk.Tk()
root.title("2D Anatomy GUI")

# Title frame
frame_title = tk.Frame(root)
frame_title.grid(row=0, column=0, padx=10, pady=10)

# Heatmap frames
frame_config_heatmap = tk.Frame(root)
frame_config_heatmap.grid(row=1, column=0, padx=10, pady=10)
frame_show_heatmap = tk.Frame(root)
frame_show_heatmap.grid(row=2, column=0, padx=10, pady=10)

# Threeaxis frames
frame_config_threeaxis = tk.Frame(root)
frame_config_threeaxis.grid(row=3, column=0, padx=10, pady=10)
frame_show_threeaxis = tk.Frame(root)
frame_show_threeaxis.grid(row=4, column=0, padx=10, pady=10)

# Readout Frame
frame_readout = tk.Frame(root)
frame_readout.grid(row=0, column=1, rowspan=5, padx=10, pady=10, sticky='ns')

"""

Threeaxis Figure Creation ___________________________________________________________________________________________"""

threeaxis_fig, axs = plt.subplots(1, 3, figsize=(10, 2), sharey=True)
threeaxis_fig.patch.set_facecolor(background_color)
threeaxis_fig.suptitle("Title", fontsize=global_fontsize, fontname=global_font)

axs[0].hist([], bins="auto", color=x_color)
axs[1].hist([], bins="auto", color=y_color)
axs[2].hist([], bins="auto", color=z_color)
axs[0].set_title(RC_title, fontsize=global_fontsize, fontname=global_font)
axs[1].set_title(DV_title, fontsize=global_fontsize, fontname=global_font)
axs[2].set_title(LR_title, fontsize=global_fontsize, fontname=global_font)
axs[0].set_xlim(0, 13000)
axs[1].set_xlim(0, 8000)
axs[2].set_xlim(0, 11400)
axs[0].set_xlabel("micrometers", fontsize=global_fontsize, fontname=global_font)
axs[1].set_xlabel("micrometers", fontsize=global_fontsize, fontname=global_font)
axs[2].set_xlabel("micrometers", fontsize=global_fontsize, fontname=global_font)
axs[0].set_ylabel("frequency", fontsize=global_fontsize, fontname=global_font)
axs[2].axvline(x=5700)

threeaxis_canvas = FigureCanvasTkAgg(threeaxis_fig, master=frame_show_threeaxis)
threeaxis_canvas.draw()
threeaxis_canvas.get_tk_widget().grid(row=0, column=0, columnspan=1, padx=5, pady=5, sticky="nsew")

"""

LRDV Heatmap Figure Creation ________________________________________________________________________________________"""

heatmap_fig, (ax_lrdv, ax_rcdv) = plt.subplots(1, 2, figsize=(10, 4))
heatmap_fig.patch.set_facecolor(background_color)
heatmap_fig.suptitle("Title", fontsize=global_fontsize, fontname=global_font)

heatmap_canvas = FigureCanvasTkAgg(heatmap_fig, master=frame_show_heatmap)
heatmap_canvas.draw()
heatmap_canvas.get_tk_widget().grid(row=0, column=0, columnspan=1, padx=5, pady=5, sticky="nsew")

"""

Widgets (frame_title) _______________________________________________________________________________________________"""

# Title of App
title = tk.Label(
    frame_title,
    text="Anatomy App",
    font=(global_font, title_fontsize)
)
title.pack(side=tk.LEFT)

# Load Data Button
load_data_button = tk.Button(
    frame_title,
    text="Load Data",
    font=(global_font, global_fontsize),
    command=load_data,
    relief=tk.RAISED,
    borderwidth=5,
    height=1
)
load_data_button.pack(side=tk.RIGHT)

"""

Widgets (frame_config_heatmap) ______________________________________________________________________________________"""

# Heatmap Command Options
options_heatmap = ["Title", "Slice"]
selected_option_heatmap = tk.StringVar(frame_config_heatmap)
selected_option_heatmap.set(options_heatmap[0])

command_name_heatmap = tk.OptionMenu(
    frame_config_heatmap,
    selected_option_heatmap,
    *options_heatmap,
    command=update_name_heatmap,
)
command_name_heatmap.config(width=15, relief="flat", bg="WHITE", font=(global_font, global_fontsize))  # Adjust width and font size
command_name_heatmap.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

# Heatmap command entry
command_value_heatmap = tk.Entry(
    frame_config_heatmap,
    width=20,
    relief=tk.FLAT,
    borderwidth=5,
    bg="WHITE",
    font=(global_font, global_fontsize)
)
command_value_heatmap.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

# Heatmap Command Button
command_button_heatmap = tk.Button(
    frame_config_heatmap,
    text="Run",
    font=(global_font, global_fontsize),
    command=run_heatmap_command,
    relief=tk.RAISED,  # Keep raised
    borderwidth=5,
    height=1
)
command_button_heatmap.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

# Heatmap Save Button
save_button_heatmap = tk.Button(
    frame_config_heatmap,
    text="Save",
    font=(global_font, global_fontsize),
    command=save_heatmap,
    relief=tk.RAISED,  # Keep raised
    borderwidth=5,
    height=1
)
save_button_heatmap.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

slice_slider = tk.Scale(
    frame_config_heatmap,
    from_=0,
    to=0,
    orient='horizontal',
    showvalue=False,
    command=on_scale
)
slice_slider.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="ew")

"""

Widgets (frame_config_threeaxis) ____________________________________________________________________________________"""

# Threeaxis command options
options_threeaxis = ["Title", "Bins"]
selected_option_threeaxis = tk.StringVar(frame_config_threeaxis)
selected_option_threeaxis.set(options_threeaxis[0])

command_name_threeaxis = tk.OptionMenu(
    frame_config_threeaxis,
    selected_option_threeaxis,
    *options_threeaxis,
    command=update_name_threeaxis,
)
command_name_threeaxis.config(width=15, relief="flat", bg="WHITE", font=(global_font, global_fontsize))  # Adjust width and font size
command_name_threeaxis.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

# Threeaxis command value
command_value_threeaxis = tk.Entry(
    frame_config_threeaxis,
    width=20,
    relief=tk.FLAT,
    borderwidth=5,
    bg="WHITE",
    font=(global_font, global_fontsize)
)
command_value_threeaxis.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

# Threeaxis command button
command_button_threeaxis = tk.Button(
    frame_config_threeaxis,
    text="Run",
    font=(global_font, global_fontsize),
    command=run_threeaxis_command,
    relief=tk.RAISED,  # Keep raised
    borderwidth=5,
    height=1
)
command_button_threeaxis.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

# Threeaxis Save Button
save_button_threeaxis = tk.Button(
    frame_config_threeaxis,
    text="Save",
    font=(global_font, global_fontsize),
    command=save_threeaxis,
    relief=tk.RAISED,  # Keep raised
    borderwidth=5,
    height=1
)
save_button_threeaxis.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

"""

Widgets (frame_readout) _____________________________________________________________________________________________"""
readout_area = tk.Text(
    frame_readout,
    wrap=tk.WORD,
    width=60,
    height=10,
    state=tk.DISABLED,
    font=(global_font, global_fontsize)  # Set font for readout area
)
readout_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(
    frame_readout,
    command=readout_area.yview
)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
readout_area.config(yscrollcommand=scrollbar.set)

"""

Start _______________________________________________________________________________________________________________"""
def on_closing():
    root.quit()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
