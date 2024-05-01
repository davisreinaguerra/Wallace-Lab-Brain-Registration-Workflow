### Described here are instructions for collecting quantitative anatomical data for individual mouse brains.  Only one brain at a time should be run through this pipeline.

# Step 1: Slice your brain

### Collect slices at a regular interval

# Step 2: Mount brains

### if you are not immunostaining, be sure to use the protocol to permeabilize cells with PBST before giving them DAPI

# Step 3: Scan slides

### Make sure your images are not overexposed

# Step 4: Create a project in Qupath containing all the slices from a single brain

# Step 5: Register your brain slices with an atlas using ABBA

### We use the program Aligning Big Brains to Atlases (ABBA).  Instructions for use can be found here: https://biop.github.io/ijp-imagetoatlas/.
### 

# Step 6: Analyze your registered Images in Qupath

## Some general notes on Qupath Use
## We are primarily using fluorescence images, which come embedded with distinct channels that are naturally separated.  This means we do not need to do the "separating stains" step which is generally required when working with brightfield.  

### https://qupath.readthedocs.io/en/stable/index.html



## Terms

### Thresholder
### Region of interest (ROI): An interesting region
### Annotation: A closed shape surrounding a particular ROI used by Qupath to denote an area to which an analysis can be applied
### Classifier: 

## Using a Pixel Classifier to dentify fluorescence intensity within ROI's



