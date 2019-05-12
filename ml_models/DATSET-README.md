# Damaged Sidewalk Dataset:

This dataset contains about 2,000 examples at an approximate 50/50 split between damaged and non-damaged sidewalks. The overall download contains ~6,000 examples as the original 2,000 examples are provided as well as segmented versions of the data based on two segmentation models. All examples are Google Street View data.

### File Structure:

```
./segmented
	/liberal
		/damaged
		/undamaged
	/standard
		/damaged
		/undamaged
./original
	/damaged
	/undamaged
```



`./segmented` - The segmented directory all images from the ./original directory that have been run through a sidewalk segmentation model.

`./segmented/liberal` - The name liberal refers to the segmentation models used for sidewalk segmentation used on the original Google Street View images. The liberal model was more generous in labeling a pixel as a part of a sidewalk. This data had a higher false positive rate.

`./segmented/standard` - The name standard refers to the segmentation model used for sidewalk segmentation on the original Google Street View images. This standard model (https://github.com/fregu856/deeplabv3) was trained as normal on the Cityscape dataset. 

`./original` - This directory contains the original Google Street View images. The damaged images were pulled based on data collected by https://projectsidewalk.io/. The undamaged images were randomly sampled from Boston streets accessed via Google Street View.

### Access the dataset

Currently the dataset is hosted on in a Google Drive Team Repo please contact this github repositories owner if you would like access.
