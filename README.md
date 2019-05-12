# BostonStreetCaster
Boston StreetCaster is an ML-based solution to automate the identification of damaged sidewalks in the City of Boston to ensure municipal services are equitably distributed to all residents.

#### There are three parts to this project:

1. The Google Street View data collection
2. The deep learning models and dataset
3. The prototype interface

### Google Street View Data Collection

As the ultimate goal of this project is to identify damaged sidewalk all across Boston we leveraged the City of Boston’s pre-existing geographic sidewalk information to partition sidewalks into GSV images. These images can then be fed into the developed ML models and audited for damage.

*[See here for more info on this section.](https://github.com/ddehueck/BostonStreetCaster/blob/master/streetview_retrieval)*

### The Machine Learning Models and Dataset

**The Machine Learning (ML) Models:** Three ML models were trained: two segmentation models and one standard CNN(ResNet) to act as a damage classifier. Data is first fed through a segmentation model to isolate the sidewalk and is then run through the damage classifer to assess any potential issues in the sidewalk.

- *[See here for more info on the segmentation models.](https://github.com/ddehueck/BostonStreetCaster/tree/master/ml_models/segment_images)*
- *[See here for more info on the damage classification model.](https://github.com/ddehueck/BostonStreetCaster/tree/master/ml_models/resnet-benchmark)*

**The Dataset:** To build a dataset of damaged sidewalks we contacted a [group](https://projectsidewalk.io/) at the University of Washington that uses Google StreetView (GSV) to find accessibility issues. With their help we were able to collect ~2,000 images of damaged sidewalks. Another ~2,000 images of undamaged sidewalks were randomly sampled from Boston streets to create a balanced dataset. All images were then segmented so any subsequently trained models only learn on sidewalks.

*[Access the dataset here and find more stats on the dataset.](https://docs.google.com/document/d/1tbSubz8HzWSgJ75nBfK65nIpwlOQ1R4lucGHUZWoS8U/edit?usp=sharing)*


### The Prototype Interface

Our prototype interface allows users to upload images to a server which then segments the sidewalk and classifies into a damaged or not damaged category. This acts as a proof-of-concept for the union of these three parts of the project.

*[Access more info on the interface here.](https://github.com/ddehueck/BostonStreetCaster/tree/master/interface)*


#### Special Thanks:

Thank you to [Project Sidewalk](https://projectsidewalk.io/) for access the data!

Thank you to the following repos that were modified for our particular ML models. https://github.com/jfzhang95/pytorch-deeplab-xception and https://github.com/fregu856/deeplabv3.
