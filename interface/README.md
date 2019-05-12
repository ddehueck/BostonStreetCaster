# BostonStreetCaster Flask App POC

This flask application is a proof-of-concept that illustrates how one would load the ML models trained into a web application. 

### Running the application:

`$ python app.py`

**Please Note:** The saved weights for the damage classification models used in this application exceeded 100 MB and store in google drive:

[The ResNet model for damage classification](https://drive.google.com/a/bu.edu/file/d/1YRgz0sdaXen8C00ZIfJE4yvLZYycbT93/view?usp=sharing) - Place it in a directory called `/saved_models` in `/damage_classification

**Also:** Upload images in multiples of 2 or an error will be encountered.

**When Segmenting Images:** Please allow time for your computer to processes the images - takes about 10 min for 4 images on a 2014 Macbook Pro.

### Screenshots:

**Upload Your Sidewalk Images:**
![](https://i.imgur.com/0Ob4aVL.png)

**Confirm Your Uploads:**
![](https://i.imgur.com/p5xlrlo.png)

**View Segmented Upload Images:**
![](https://i.imgur.com/kntHCAd.png)

**View Summary With Predicitions:**
![](https://i.imgur.com/2B1VbJV.png)

### Dependencies:

 - `Flask`
 - `opencv-python`
 - `torch`
 - `torchvision`
 - `numpy`
