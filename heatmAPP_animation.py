from PIL import Image
import easygui
import os

def create_gif_from_png(folder_path, output_filename, frame_duration):
    # Get a list of PNG files in the folder, sorted by name
    images = sorted([img for img in os.listdir(folder_path) if img.endswith('.png')])

    # Load the images into a list
    frames = [Image.open(os.path.join(folder_path, image)) for image in images]

    # Create a reversed list of the frames (excluding the last frame to avoid duplication)
    reversed_frames = frames[-2::-1]

    # Combine the original frames with the reversed frames
    all_frames = frames + reversed_frames

    # Save the frames as a GIF
    all_frames[0].save(os.path.join(folder_path, output_filename),
                       save_all=True,
                       append_images=all_frames[1:],
                       duration=frame_duration,
                       loop=0)

animation_folder_path = easygui.diropenbox(msg="Select the folder containing the PNG files")
animation_filename = easygui.enterbox("File name","Input")
frame_duration = 100  # Duration per frame in milliseconds
output_filename = f"{animation_filename}.gif"  # Specify the output GIF file name

create_gif_from_png(folder_path, output_filename, frame_duration)
