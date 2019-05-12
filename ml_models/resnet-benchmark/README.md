# Damage Classification Model - The ResNet Benchmark

### Training:

Before running you will need to place your data in the same directory as `train.py` following the PyTorch ImageFolder dataset structure:

```
./data
	/damaged_images
	/nondamaged_images
```

**Run:** ``$ python train.py``

**Requires:** `torch>=0.4.1 torchvision>=0.2.1`

### Loading the Models:

The train script automatically saves checkpoint data and the resulting model. We follow the guidelines outline: https://pytorch.org/tutorials/beginner/saving_loading_models.html

### Dataset Trained On:
[See here for more info on the dataset](https://github.com/ddehueck/BostonStreetCaster/blob/master/ml_models/DATASET-README.md)
