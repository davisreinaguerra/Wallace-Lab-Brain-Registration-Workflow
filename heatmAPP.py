# Custom
from heatmAPP_peripherals import *

from brainrender import Scene
import numpy as np
import pandas as pd
import tkinter as tk
import easygui

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.colors import ListedColormap

from scipy.stats import gaussian_kde
from scipy.ndimage import gaussian_filter


"""
Global Variables ____________________________________________________________________________________________________"""

scene = Scene(atlas_name="allen_mouse_25um")
global_font = "Consolas"
global_fontsize = 12
title_fontsize = 20
background_color = "#F0F0F0"
heatmap_name = "Title"                                                                 # default
threeaxis_name = "Title"                                                               # default
data_um = None
mesh_verts = []
title = None
default_cmap = "plasma"
current_cmap = None
x_color = "#58229D"
y_color = "#BB8651"
z_color = "#51AEBB"
RC_title = "R <---------------> C"
DV_title = "D <---------------> V"
LR_title = "L <-------M-------> R"

# Things to declare globally
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
global_min = None
global_max = None
previous_lines = []
previous_text = []


"""
Global Functions ____________________________________________________________________________________________________"""

def add_message(message):
    readout_area.config(state=tk.NORMAL)
    readout_area.insert(tk.END, message + "\n")
    readout_area.see(tk.END)
    readout_area.config(state=tk.DISABLED)

"""
Callback Functions __________________________________________________________________________________________________"""

def load_data():
    global data_um
    global mesh_verts
    global default_cmap
    global rc_limits
    global dv_limits
    global lr_limits
    global rc_data
    global dv_data
    global lr_data
    global rc_shadow
    global dv_shadow
    global lr_shadow
    global global_min
    global global_max

    """
    Format Data_______________________________________________________________________________________"""
    file_path = easygui.fileopenbox()  # get file path
    data_um = pd.read_csv(file_path) * 1000  # read mm data from csv file
    rc_data = data_um["Allen CCFv3 X mm"]  # Allen X = RC
    dv_data = data_um["Allen CCFv3 Y mm"]  # Allen Y = DV
    lr_data = data_um["Allen CCFv3 Z mm"]  # Allen Z = LR

    """
    Format Shadow ____________________________________________________________________________________"""
    structure_ids = easygui.enterbox("Names of Structures:","Input")
    structure_ids_array = structure_ids.split(",")
    add_message(f"Structure ID's: {structure_ids_array}")
    for entry in structure_ids_array:
        structure = scene.add_brain_region(entry)
        try:
            new_mesh = structure.mesh
            subdivided_new_mesh = new_mesh.subdivide(method=1, n=3)
            subdivided_new_mesh_verts = subdivided_new_mesh.vertices
            mesh_verts.append(subdivided_new_mesh_verts)
        except:
            add_message(f"No vertices found for structure: {entry}")
    if len(mesh_verts) == 0:
        add_message("No mesh vertices found. Please check the structure IDs.")
        return
    mesh_verts = np.concatenate(mesh_verts, axis=0)
    rc_shadow = mesh_verts[:, 0]
    dv_shadow = mesh_verts[:, 1]
    lr_shadow = mesh_verts[:, 2]

    """
    Format Shadow ___________________________________________________________________________________ """
    rc_limits = [np.min(mesh_verts[:, 0]), np.max(mesh_verts[:, 0])]
    dv_limits = [np.min(mesh_verts[:, 1]), np.max(mesh_verts[:, 1])]
    lr_limits = [np.min(mesh_verts[:, 2]), np.max(mesh_verts[:, 2])]

    # Plot_heatmap _____________________________________________________________________________________________________
    plot_shadowed_heatmap(
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
        cmap_template = default_cmap,
        bin_edges = None,
        binned_lr_data = None,
        binned_dv_data = None,
        binned_lr_shadow = None,
        binned_dv_shadow = None,
        global_max = None,
        global_min = None
    )
    heatmap_canvas.draw()

    # Get the min and max
    data_hist_lrdv, xedges_lrdv, yedges_lrdv = np.histogram2d(
        lr_data,
        dv_data,
        bins=100,
        range=[[lr_limits[0], lr_limits[1]], [dv_limits[0], dv_limits[1]]]
    )
    data_hist_lrdv = gaussian_filter(data_hist_lrdv, sigma=1)
    global_min = data_hist_lrdv.min()
    global_max = data_hist_lrdv.max()

    # Threeaxis ________________________________________________________________________________________________________
    axs[0].hist(data_um["Allen CCFv3 X mm"], bins="auto", color=x_color)
    axs[1].hist(data_um["Allen CCFv3 Y mm"], bins="auto", color=y_color)
    axs[2].hist(data_um["Allen CCFv3 Z mm"], bins="auto", color=z_color)
    axs[0].set_xlim(rc_limits[0], rc_limits[1])
    axs[1].set_xlim(dv_limits[0], dv_limits[1])
    axs[2].set_xlim(lr_limits[0], lr_limits[1])

    threeaxis_canvas.draw()
    add_message("Data Loaded")

def update_heatmap(val):
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
    global previous_text
    global current_cmap
    global global_max
    global global_min

    # get rid of old axvlines
    for line in previous_lines:
        line.remove()
    previous_lines.clear()

    # get rid of old ranges
    for text in previous_text:
        text.remove()
    previous_text.clear()

    try:
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

        n_cells = len(binned_lr_data)

        binned_dv_shadow = binned_shadow[:, 1]
        binned_lr_shadow = binned_shadow[:, 2]

        plot_shadowed_heatmap(
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
            cmap_template=current_cmap,
            bin_edges=current_bin_edges,
            binned_lr_data=binned_lr_data,
            binned_dv_data=binned_dv_data,
            binned_lr_shadow=binned_lr_shadow,
            binned_dv_shadow=binned_dv_shadow,
            global_max = global_max,
            global_min = global_min
        )

        # axvlines for rcdv
        rostral = ax_rcdv.axvline(x=current_bin_edges[0], color="black")
        caudal = ax_rcdv.axvline(x=current_bin_edges[1], color="black")
        previous_lines.extend([rostral, caudal])

        # text for lrdv
        rounded_rostral_lim_mm = round((current_bin_edges[0] / 1000), 1)
        rounded_caudal_lim_mm = round((current_bin_edges[1] / 1000), 1)
        range_text = ax_lrdv.text(
            0.02,  # relative X
            0.95,  # relative Y
            f"Range: {rounded_rostral_lim_mm}mm - {rounded_caudal_lim_mm}mm",
            color='black',
            transform=ax_lrdv.transAxes,
            zorder=10
        )
        n_cells_text = ax_lrdv.text(
            0.02,  # relative X
            0.90,  # relative Y
            f"n_Cells: {n_cells}",
            color="black",
            transform=ax_lrdv.transAxes,
            zorder=10
        )
        previous_text.extend([range_text, n_cells_text])

        heatmap_canvas.draw()
    except:
        plot_shadowed_heatmap(
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
            cmap_template=current_cmap,
            bin_edges=None,
            binned_lr_data=None,
            binned_dv_data=None,
            binned_lr_shadow=None,
            binned_dv_shadow=None,
            global_min = None,
            global_max = None
        )

def update_name_heatmap(selection):
    global heatmap_name
    heatmap_name = selection

def update_name_threeaxis(selection):
    global threeaxis_name
    threeaxis_name = selection

def run_heatmap_command():
    global rc_limits
    global dv_limits
    global lr_limits
    global n_bins
    global bin_edges
    global update_heatmap
    global current_cmap

    selected_name = heatmap_name
    value = command_value_heatmap.get().strip()
    if selected_name == "Title":
        heatmap_fig.suptitle(value, fontsize=global_fontsize)
        heatmap_canvas.draw()
        add_message("Changed Heatmap Title")
    elif selected_name == "Slice":
        n_bins = int(value)
        bin_edges = np.round(np.linspace(rc_limits[0], rc_limits[1], n_bins + 1)).astype(int)
        slice_slider.config(from_=0, to_=n_bins-1, showvalue=False)
        update_heatmap(0)
        add_message("Sliced!")
    elif selected_name == "Change Cmap":
        try:
            current_cmap = value
            update_heatmap(0)
        except:
            add_message("entered colormap not found")
    else:
        print("error: no entry")

def run_threeaxis_command():
    selected_name = threeaxis_name
    value = command_value_threeaxis.get().strip()
    if selected_name == "Title":
        threeaxis_fig.suptitle(value, fontsize=global_fontsize)
        threeaxis_canvas.draw()
        add_message("Changed Threeaxis Title")
    elif selected_name == "n_bins":
        value_int = int(value)
        change_bin_size(value_int)
    else:
        print("error: no entry")

def save_heatmap():
    add_message("Under construction save heatmap")
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
    add_message("Under construction save threeaxis")




"""

App Creation ________________________________________________________________________________________________________"""

root = tk.Tk()
root.title("Mouse Neuroanatomy HeatMapp")

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

Heatmap Figure Creation _____________________________________________________________________________________________"""

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
    text="Mouse Neuroanatomy HeatMapp",
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
load_data_button.pack(side=tk.LEFT)

"""

Widgets (frame_config_heatmap) ______________________________________________________________________________________"""

# Heatmap Command Options
options_heatmap = ["Title", "Slice", "Change Cmap"]
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
    command=update_heatmap
)
slice_slider.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="ew")

"""

Widgets (frame_config_threeaxis) ____________________________________________________________________________________"""

# Threeaxis command options
options_threeaxis = ["Title", "n_ins"]
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
