# BostonStreetCaster ML Models

We solve two problems with the ML models in this repo: sidewalk segmentation and sidewalk damage classification.

### Sidewalk Damage Classification

**Input:** A sidewalk segmented out of a Google Street View image.

**Output:** 0 or 1 corresponding to Damaged or Not Damged respectively.

We treat this problem as a standard image classification problem and use the [ResNet architecture](https://arxiv.org/pdf/1512.03385.pdf) from the PyTorch model zoo. The model was trained on a custom made dataset - [see here for more info on the dataset](#)

[See here for a futher breakdown of the ML models.](#)

### Sidewalk Segmentation

**Input:** A Google Street View image.

**Output:** An image containing just pixels determined to be from a sidewalk.

We trained two models, a standard model and a liberal model. The standard model was trained with standard class balances on the [Cityscapes Dataset](https://www.cityscapes-dataset.com/) while the liberal model was trained on the same dataset but with a class balance equaling the likelihood that a pixel is a sidewalk vs not a sidewalk (this leads to a higher false positive rate).

- [See here for a futher breakdown on the standard model.](#)
- [See here for a futher breakdown on the liberal model.](#)
