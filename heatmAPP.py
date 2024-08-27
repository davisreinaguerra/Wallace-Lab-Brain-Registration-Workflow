# Custom Libraries
from heatmAPP_peripherals import *

# Premade libraries
from brainrender import Scene
import numpy as np
import pandas as pd
import tkinter as tk
import easygui
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.colors import ListedColormap
import matplotlib.ticker as ticker
from scipy.ndimage import gaussian_filter


"""
Global Variables ____________________________________________________________________________________________________"""

scene = Scene(atlas_name="allen_mouse_25um")
global_font = "Consolas"
global_fontsize = 12
title_fontsize = 32
background_color = "#FFFFFF"
selection_name = None
data_um = None
mesh_verts = []
title = None
default_cmap = "twilight"
current_cmap = "twilight"
x_color = "#6A0DAD"
y_color = "#6BBF59"
z_color = "#87CEEB"
RC_title = "Rostral < - > Caudal"
DV_title = "Dorsal < - > Ventral"
LR_title = "L < M > R"

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
global_max_scaler = 1
open_filename = None
mm_range = None
n_cells = None

previous_lines = []
previous_text = []

"""
Global Functions 
________________________________________________________________________________________________________________________
"""

def add_message(message):
    readout_area.config(state=tk.NORMAL)
    readout_area.insert(tk.END, message + "\n")
    readout_area.see(tk.END)
    readout_area.config(state=tk.DISABLED)

"""
Callback Functions 
________________________________________________________________________________________________________________________
"""

def update_heatmap(val = None):
    # Raw Data
    global data_um
    global mesh_verts
    # Coordinates per axis
    global rc_data
    global dv_data
    global lr_data
    # Shadows per axis
    global rc_shadow
    global dv_shadow
    global lr_shadow
    # Raw Data
    global rc_limits
    global dv_limits
    global lr_limits
    # Colormaps
    global default_cmap
    global current_cmap
    global global_min
    global global_max
    global global_max_scaler
    # Updatable Text
    global previous_lines
    global previous_text
    # save_filename vars
    global mm_range
    global n_cells
    # Save
    global open_filename

    # get rid of old axvlines
    for line in previous_lines:
        line.remove()
    previous_lines.clear()

    # get rid of old ranges
    for text in previous_text:
        text.remove()
    previous_text.clear()

    try:# If Data has been Loaded and Binned
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

        number_cells = len(binned_lr_data)

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
            global_min = global_min,
            global_max_scaler=global_max_scaler
        )

        # axvlines for rcdv
        rostral = ax_rcdv.axvline(x=current_bin_edges[0], color="black")
        caudal = ax_rcdv.axvline(x=current_bin_edges[1], color="black")
        previous_lines.extend([rostral, caudal])

        try:
            # text for lrdv
            rounded_rostral_lim_mm = round((current_bin_edges[0] / 1000), 1)
            rounded_caudal_lim_mm = round((current_bin_edges[1] / 1000), 1)
            mm_range = f"{rounded_rostral_lim_mm}mm_{rounded_caudal_lim_mm}mm"
            range_text = ax_lrdv.text(
                0.02,  # relative X
                0.95,  # relative Y
                mm_range,
                color='black',
                transform=ax_lrdv.transAxes,
                zorder=10
            )
            n_cells = f"{number_cells}_cells"
            n_cells_text = ax_lrdv.text(
                0.02,  # relative X
                0.90,  # relative Y
                n_cells,
                color="black",
                transform=ax_lrdv.transAxes,
                zorder=10
            )
            previous_text.extend([range_text, n_cells_text])
        except:
            add_message("didnt work")

        heatmap_canvas.draw()
        
    except: # If no data has been Loaded
        # Format Data
        file_path = easygui.fileopenbox()  # get file path
        open_filename = os.path.splitext(os.path.basename(file_path))[0]  # get name of file without extension
        data_um = pd.read_csv(file_path) * 1000  # read mm data from csv file
        rc_data = data_um["Allen CCFv3 X mm"]  # Allen X = RC
        dv_data = data_um["Allen CCFv3 Y mm"]  # Allen Y = DV
        lr_data = data_um["Allen CCFv3 Z mm"]  # Allen Z = LR

        # Gather a List of Structure Names
        structure_ids = easygui.enterbox("Names of Structures:", "Input")
        structure_ids_array = structure_ids.split(",")
        add_message(f"Structure ID's: {structure_ids_array}")

        # Gather the Coordinates of Every Listed Structure
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

        # Calculate shadow coordinates
        rc_shadow = mesh_verts[:, 0]
        dv_shadow = mesh_verts[:, 1]
        lr_shadow = mesh_verts[:, 2]

        # Calculate limits of Shadow
        rc_limits = [np.min(mesh_verts[:, 0]), np.max(mesh_verts[:, 0])]
        dv_limits = [np.min(mesh_verts[:, 1]), np.max(mesh_verts[:, 1])]
        lr_limits = [np.min(mesh_verts[:, 2]), np.max(mesh_verts[:, 2])]

        # Plot
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
            cmap_template=default_cmap,
            bin_edges=None,
            binned_lr_data=None,
            binned_dv_data=None,
            binned_lr_shadow=None,
            binned_dv_shadow=None,
            global_max=None,
            global_min=None,
            global_max_scaler=global_max_scaler
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
        axs[0].hist(data_um["Allen CCFv3 X mm"], bins="auto", color=x_color, density=True)
        axs[1].hist(data_um["Allen CCFv3 Y mm"], bins="auto", color=y_color, density=True)
        axs[2].hist(data_um["Allen CCFv3 Z mm"], bins="auto", color=z_color, density=True)
        axs[0].set_xlim(rc_limits[0], rc_limits[1])
        axs[1].set_xlim(dv_limits[0], dv_limits[1])
        axs[2].set_xlim(lr_limits[0], lr_limits[1])
        axs[0].set_xticks([rc_limits[0], rc_limits[1]])
        axs[1].set_xticks([dv_limits[0], dv_limits[1]])
        axs[2].set_xticks([lr_limits[0], 5700, lr_limits[1]])
        axs[0].xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x / 1000:.1f}'))
        axs[1].xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x / 1000:.1f}'))
        axs[2].xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x / 1000:.1f}'))
        axs[0].set_yticks([])
        axs[2].invert_xaxis() # flip left and right

        threeaxis_canvas.draw()
        add_message("Data Loaded")

def update_selection_name(selection):
    global selection_name
    selection_name = selection

def run_command():
    global rc_limits
    global dv_limits
    global lr_limits
    global data_um
    global n_bins
    global bin_edges
    global update_heatmap
    global current_cmap
    global selection_name
    global global_max_scaler

    selected_name = selection_name
    value = command_value.get().strip()
    if selected_name == "Slice By":
        um_per_slice = int(value)
        n_bins = int(np.round((rc_limits[1]-rc_limits[0]) / um_per_slice))
        bin_edges = np.round(np.linspace(rc_limits[0], rc_limits[1], n_bins + 1)).astype(int)
        slice_slider.config(from_=0, to_=n_bins - 1, showvalue=False)
        update_heatmap(0)
        add_message(f"Slice_size ~ {value}um, n_bins = {n_bins}")
    elif selected_name == "Slice Into":
        n_bins = int(value)
        bin_edges = np.round(np.linspace(rc_limits[0], rc_limits[1], n_bins + 1)).astype(int)
        slice_slider.config(from_=0, to_=n_bins-1, showvalue=False)
        update_heatmap(0)
        add_message("Sliced!")
    elif selected_name == "Histogram Bins":
        value_int = int(value)
        working_xlim_X = axs[0].get_xlim()
        working_xlim_Y = axs[1].get_xlim()
        working_xlim_Z = axs[2].get_xlim()
        axs[0].clear()
        axs[1].clear()
        axs[2].clear()
        axs[0].hist(data_um["Allen CCFv3 X mm"], bins=value_int, color=x_color, density=True)
        axs[1].hist(data_um["Allen CCFv3 Y mm"], bins=value_int, color=y_color, density=True)
        axs[2].hist(data_um["Allen CCFv3 Z mm"], bins=value_int, color=z_color, density=True)
        axs[0].xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x / 1000:g}'))
        axs[1].xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x / 1000:g}'))
        axs[2].xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x / 1000:g}'))
        axs[0].set_title(RC_title)
        axs[1].set_title(DV_title)
        axs[2].set_title(LR_title)
        axs[0].set_xlim(working_xlim_X)
        axs[1].set_xlim(working_xlim_Y)
        axs[2].set_xlim(working_xlim_Z)
        axs[0].set_xlabel("micrometers", fontsize=global_fontsize, fontname=global_font)
        axs[1].set_xlabel("micrometers", fontsize=global_fontsize, fontname=global_font)
        axs[2].set_xlabel("micrometers", fontsize=global_fontsize, fontname=global_font)
        axs[0].set_ylabel("frequency", fontsize=global_fontsize, fontname=global_font)
        axs[2].axvline(x=5700)
        threeaxis_canvas.draw()
    elif selected_name == "Scale Global Max":
        try:
            global_max_scaler = float(value)
            update_heatmap(0)
            add_message("Scaled!")
        except:
            add_message("You gotta slice first")
    else:
        add_message("error: no entry")

def save_heatmap():
    global open_filename
    global mm_range
    global n_cells
    global n_bins
    global update_heatmap

    save_dir = easygui.diropenbox(title="Select Directory to Save Figures")
    os.chdir(save_dir)

    try:
        for bin in range(n_bins):
            update_heatmap(bin)
            str_range = str(mm_range)
            str_cells = str(n_cells)
            save_fig_filename = f"{open_filename}_{str_range}_{str_cells}.png"
            add_message(f"Saved: {save_fig_filename}")
            heatmap_fig.savefig(save_fig_filename)
        add_message("Heatmaps Saved")
    except:
        update_heatmap(0)
        heatmap_fig.savefig(open_filename + "_overview.png")
        add_message("Heatmap Saved")

def save_threeaxis():
    save_dir = easygui.diropenbox(title="Select Directory to Save Figures")
    os.chdir(save_dir)

    threeaxis_fig.savefig(open_filename + "_threeaxis_histogram.png")
    add_message("Threeaxis Saved")




"""
App Creation 
________________________________________________________________________________________________________________________
"""

# Create Tkinter Application
root = tk.Tk()
root.title("Mouse Neuroanatomy HeatMapp")

root.rowconfigure(3, weight=1)

# Title Frame
frame_title = tk.Frame(root)
frame_title.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Configure Frame
frame_config = tk.Frame(root)
frame_config.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

# Heatmap Frame
frame_show_heatmap = tk.Frame(root, bd=5, relief=tk.GROOVE)
frame_show_heatmap.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

# Threeaxis Frame
frame_show_threeaxis = tk.Frame(root, bd=5, relief=tk.GROOVE)
frame_show_threeaxis.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

# Readout Frame
frame_readout = tk.Frame(root)
frame_readout.grid(row=0, column=1, rowspan=5, padx=10, pady=10, sticky='ns')

"""
Heatmap Figure Creation ________________________________________________________________________________________________

"""
heatmap_fig, (ax_lrdv, ax_rcdv) = plt.subplots(1, 2, figsize=(10, 4.5))
heatmap_fig.patch.set_facecolor(background_color)
heatmap_fig.tight_layout(pad=2.0)
ax_lrdv.set_facecolor("white")
ax_rcdv.set_facecolor("white")


heatmap_canvas = FigureCanvasTkAgg(heatmap_fig, master=frame_show_heatmap)
heatmap_canvas.draw()
heatmap_canvas.get_tk_widget().grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

"""
Threeaxis Figure Creation ______________________________________________________________________________________________

"""

threeaxis_fig, axs = plt.subplots(1, 3, figsize=(10, 3), sharey=True)
threeaxis_fig.patch.set_facecolor(background_color)
threeaxis_fig.tight_layout(pad=2.0)

axs[0].hist([], bins="auto", color=x_color)
axs[1].hist([], bins="auto", color=y_color)
axs[2].hist([], bins="auto", color=z_color)
axs[0].xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x / 1000:g}'))
axs[1].xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x / 1000:g}'))
axs[2].xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x / 1000:g}'))
axs[0].set_title(RC_title)
axs[1].set_title(DV_title)
axs[2].set_title(LR_title)
axs[0].set_xlim(0, 13000)
axs[1].set_xlim(0, 8000)
axs[2].set_xlim(0, 11400)
axs[0].set_xlabel("millimeters", fontsize=global_fontsize, fontname=global_font)
axs[1].set_xlabel("millimeters", fontsize=global_fontsize, fontname=global_font)
axs[2].set_xlabel("millimeters", fontsize=global_fontsize, fontname=global_font)
axs[0].set_xticks([])
axs[1].set_xticks([])
axs[2].set_xticks([])

axs[0].set_yticks([])
axs[0].set_ylabel("cell density (norm)", fontsize=global_fontsize, fontname=global_font)
axs[2].axvline(x=5700)


axs[2].invert_xaxis() # flip left and right

threeaxis_canvas = FigureCanvasTkAgg(threeaxis_fig, master=frame_show_threeaxis)
threeaxis_canvas.draw()
threeaxis_canvas.get_tk_widget().grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

"""

Widgets (frame_title) _______________________________________________________________________________________________"""

# Title of App
title = tk.Label(
    frame_title,
    text="HeatMapp",
    font=(global_font, title_fontsize)
)
title.pack(side=tk.LEFT, padx=10)

# Load Data Button
load_data_button = tk.Button(
    frame_title,
    text="Load Data",
    font=(global_font, global_fontsize),
    command=update_heatmap,
    relief=tk.RAISED,
    borderwidth=5,
    height=1
)
load_data_button.pack(side=tk.RIGHT, padx=10)

"""

Widgets (frame_config) ______________________________________________________________________________________"""

# Heatmap Command Options
options_heatmap = ["select...", "Slice Into", "Slice By", "Histogram Bins", "Scale Global Max"]
selected_option_heatmap = tk.StringVar(frame_config)
selected_option_heatmap.set(options_heatmap[0])

command_name = tk.OptionMenu(
    frame_config,
    selected_option_heatmap,
    *options_heatmap,
    command=update_selection_name,
)
command_name.config(width=15, relief="flat", bg="WHITE", font=(global_font, global_fontsize))  # Adjust width and font size
command_name.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

# Command Entry
command_value = tk.Entry(
    frame_config,
    width=30,
    relief=tk.FLAT,
    borderwidth=5,
    bg="WHITE",
    font=(global_font, global_fontsize)
)
command_value.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

# Command Button
command_button = tk.Button(
    frame_config,
    text="Run",
    font=(global_font, global_fontsize),
    command=run_command,
    relief=tk.RAISED,  # Keep raised
    borderwidth=5,
    height=1
)
command_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

# Heatmap Save Button
save_button_heatmap = tk.Button(
    frame_config,
    text="Save Heatmap",
    font=(global_font, global_fontsize),
    command=save_heatmap,
    relief=tk.RAISED,  # Keep raised
    borderwidth=5,
    height=1
)
save_button_heatmap.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

# Threeaxis Save Button
save_button_threeaxis = tk.Button(
    frame_config,
    text="Save Histogram",
    font=(global_font, global_fontsize),
    command=save_threeaxis,
    relief=tk.RAISED,  # Keep raised
    borderwidth=5,
    height=1
)
save_button_threeaxis.grid(row=0, column=4, padx=5, pady=5, sticky="ew")

# Slice Slider
slice_slider = tk.Scale(
    frame_config,
    from_=0,
    to=0,
    orient='horizontal',
    showvalue=False,
    command=update_heatmap
)
slice_slider.grid(row=1, column=0, columnspan=5, padx=5, pady=5, sticky="ew")

"""

Widgets (frame_readout) _____________________________________________________________________________________________"""
readout_area = tk.Text(
    frame_readout,
    wrap=tk.WORD,
    width=70,
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