### Described here are instructions for collecting quantitative anatomical data for individual mouse brains.  Only one brain at a time should be run through this pipeline.

# Step 1: Slice your brain

### The first step is to slice your brain however you see fit.  Because the most common cutting plane for histology is coronal we will show the process using coronal slides but keep in mind that all of these steps can be accomplished with sagittal and horizontal sections as well, and although you should do everything you can to ensure an even cutting angle (see pictures below, it is best to start with a reasonably even brain).  

![image](https://github.com/davisreinaguerra/Wallace-Lab-Brain-Registration-Workflow/assets/105831652/e5fd0bf1-04c6-465b-aaa9-ab49e6b798db)
![image](https://github.com/davisreinaguerra/Wallace-Lab-Brain-Registration-Workflow/assets/105831652/84bb88c1-e769-4cca-b18b-52e313ba1fdd)




# Step 2: Mount brains

### if you are not immunostaining, be sure to use the protocol to permeabilize cells with PBST before giving them DAPI.

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

### This page shows you how to manage your registered slices in QuPath: https://abba-documentation.readthedocs.io/en/latest/tutorial/4_qupath_analysis.html
### ABBA QuPath Registration Explorer: https://github.com/nickdelgrosso/ABBA-QuPath-RegistrationAnalysis


## Terms

### Thresholder
### Region of interest (ROI): An interesting region
### Annotation: A closed shape surrounding a particular ROI used by Qupath to denote an area to which an analysis can be applied
### Classifier: 

## Using a Pixel Classifier to quantify fluorescence intensity within ROI's



