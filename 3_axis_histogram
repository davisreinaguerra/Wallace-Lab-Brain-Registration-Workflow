import tkinter as tk
import easygui
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import matplotlib.pyplot as plt

# Global Varibles ______________________________________________________
background_color_all = "whitesmoke"
name = None
data_um = None
x_color = "blue"
y_color = "red"
z_color = "green"

'''
Add something that can get the bounds of any structure and create a dataframe as follows

structure name = "GPi"
    Max      Min
X   9809     78687
Y   9080     79889
Z   9087     8987

such that you can set the limit of the x axes to the extent of that structure   
'''


# Command Functions __________________________________________________
def change_title_to(value):
    fig.suptitle(value)
    canvas.draw()

def change_bin_size(value):
    axs[0].clear()
    axs[1].clear()
    axs[2].clear()

    axs[0].hist(data_um["Allen CCFv3 X mm"], bins=value, color=x_color)
    axs[1].hist(data_um["Allen CCFv3 Y mm"], bins=value, color=y_color)
    axs[2].hist(data_um["Allen CCFv3 Z mm"], bins=value, color=z_color)
    canvas.draw()

def update_name(selection):
    global name
    name = selection

def load_file():
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
    if selected_name == "title":
        change_title_to(value)
    elif selected_name == "numBins":
        value_int = int(value)
        change_bin_size(value_int)
    else:
        print("error: no entry")

# Initiate ____________________________________________________________
frame = tk.Tk()
frame.title("Anatomy Histogram Creator")
frame.configure(bg=background_color_all)

# Create Hist _________________________________________________________
fig, axs = plt.subplots(1, 3, figsize=(15, 5), sharey=True)

# X position
axs[0].hist([], bins="auto", color="blue")
axs[1].hist([], bins="auto", color="red")
axs[2].hist([], bins="auto", color="green")

axs[0].set_title("X")
axs[1].set_title("Y")
axs[2].set_title("Z")

# z position
axs[2].set_title("Z")

canvas = FigureCanvasTkAgg(fig, master=frame)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

"""

Widgets

"""

# Command Name ________________________________________________________
options = ["title", "numBins"]
selected_option = tk.StringVar(frame)
selected_option.set(options[0])

command_name_optionmenu = tk.OptionMenu(
    frame,
    selected_option,
    *options,
    command=update_name
)
command_name_optionmenu.pack(side=tk.LEFT,padx=5,pady=5)


# Command Value ________________________________________________________
command_value_entry = tk.Entry(
    frame,
    width=30,
    relief=tk.RIDGE,
    borderwidth=5,
    bg="lightgrey",
    font=("Arial",12)
)
command_value_entry.pack(side=tk.LEFT,padx=5,pady=5)

# Run Command Button ________________________________________________
command_button = tk.Button(
    frame,
    text="Run Command",
    command=run_command,
    relief=tk.RAISED,
    borderwidth=5
)
command_button.pack(side=tk.LEFT,padx=5,pady=5)

# load Button ________________________________________________
load_button = tk.Button(
    frame,
    text="Load File",
    command=load_file,
    relief=tk.RAISED,
    borderwidth=5
)
load_button.pack(side=tk.LEFT,padx=5,pady=5)



plt.close()
frame.mainloop()
