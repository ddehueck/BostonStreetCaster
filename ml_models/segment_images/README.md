# BostonStreetCaster Segment Images

**Input:** A Google Street View image.

**Output:** An image containing just pixels determined to be from a sidewalk.

We trained two models, a standard model and a liberal model. The standard model was trained with standard class balances on the [Cityscapes Dataset](https://www.cityscapes-dataset.com/) while the liberal model was trained on the same dataset but with a class balance equaling the likelihood that a pixel is a sidewalk vs not a sidewalk (this leads to a higher false positive rate).

- [See here for a futher breakdown on the standard model.](https://github.com/ddehueck/BostonStreetCaster/tree/master/ml_models/segment_images/standard)
- [See here for a futher breakdown on the liberal model.](https://github.com/ddehueck/BostonStreetCaster/tree/master/ml_models/segment_images/liberal)
