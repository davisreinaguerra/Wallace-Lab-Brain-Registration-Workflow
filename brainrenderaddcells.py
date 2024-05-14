import numpy as np
import pandas as pd
from brainrender import Scene, actors
from brainrender.actors import Points
from brainrender import settings

def csv_to_numpy_array(file_path):
    # Use pandas to read the CSV file
    df = pd.read_csv(file_path)
    # Convert the DataFrame to a NumPy array
    numpy_array = df.to_numpy()
    return numpy_array

file_path = 'data.csv'  # Replace 'your_file.csv' with the path to your CSV file
numpy_array = csv_to_numpy_array(file_path)
numpy_array = numpy_array*1000
cell_coordinates = np.array(numpy_array)

settings.SHADER_STYLE = "plastic"
scene = Scene(atlas_name="allen_mouse_25um")
scene.add_brain_region("STRd", "GPi", "GPe", "LH", alpha = 0.15)
print(cell_coordinates)
cells = actors.Points(cell_coordinates,  name="CELL", colors="red")
scene.add(cells)
scene.render()
