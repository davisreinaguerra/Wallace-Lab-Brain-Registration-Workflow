from brainrender import Animation, Scene, settings
from pathlib import Path

settings.SHOW_AXES = False

scene = Scene(atlas_name="allen_mouse_25um")

# Tracts__________________________________________________________________________________
tracts = ["cpd", "int"]
scene.add_brain_region(*tracts, alpha=0.4, silhouette=False, color="white")

# Structures______________________________________________________________________________
structures = [
    "STRd",
    "STRv",
    "GPe",
    "GPi",
    "STN",
    "SNr",
    "VAL",
    "LH",
    "VM",
    "SNc",
    "VTA",
    "MH",
    "AUD",
    "VIS",

]
scene.add_brain_region(*structures, alpha=1.0, silhouette=True)

def slice_callback(scene, framen, totframes):
    # Get new slicing plane
    fact = framen / totframes
    shape_um = scene.atlas.shape_um
    # Multiply by fact to move the plane, add buffer to go past the brain
    point = [(shape_um[0] + 500) * fact, shape_um[1] // 2, shape_um[2] // 2]
    plane = scene.atlas.get_plane(pos=point, norm=(1, 0, 0))

    scene.slice(plane)

anim = Animation(
    scene, Path.cwd(), "animation_2", size=None
)

# Specify camera pos and zoom and the first key frame and add a callback
anim.add_keyframe(0, camera="frontal", zoom=1, callback=slice_callback)

# Make a five-second long video at 10 fps (50 frames total)
anim.make_video(duration=5, fps=10, fix_camera=True)
