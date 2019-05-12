# BostonStreetCaster Liberal Segmentation Model

### /pytorch-deeplab-xception

This is the model used when retraining under equal class likelihoods with the two classes sidewalk and not sidewalk. This is a modified version of: [https://github.com/jfzhang95/pytorch-deeplab-xception]()


### /segmentation_inference

Place images to segment in the `/test_data/0` directory and run `$ python infer.py`. The segmented images will then populate a new directory.

**Note:** The saved model for segmentation inference can be [downloaded here](https://drive.google.com/open?id=1vcqrZH9d1W-A2M684YIH176NdFy897Dx). Place it in the same directory as infer.py.


**Both Requires**: `torch>=0.4.1 torchvision>=0.2.1`

