# Sidewalk Dataset Preprocessing

In this document we'll describe how we preprocess given dataset, and derive parameter sets for querying Google's [street view API](https://developers.google.com/maps/documentation/streetview/intro) sidewalk images.

## About Dataset and Resource

We have our sidewalk and street data from Boston Hack 2018's dataset. The whole dataset can be obtained from [this project description] (https://docs.google.com/document/d/1jS3QsgjQLZyYoZzs0WbrA_SrOWAhEUv6Cc_a8X0oHJA/). The street dataset consists of line segments of streets in Boston; and sidewalk dataset contains shape polygons of planned sidewalk blocks. Both datasets use coordinate system under *EPSG:6492*'s ([description](https://epsg.io/6492)) projection settings. 

### Coordinate Conversion

Because Google's street view API only accept *WGS84* (worldwide coordinate system, [ref](https://en.wikipedia.org/wiki/World_Geodetic_System)), while the dataset uses another coordinate system, we need to transform location coordinates beforehand. There are several Python libraries supporting coordinate conversion, such as `pyproj`. However, we found that transfomation result from local machine suffers from significant numeral error, which can't be directly applied in further task.

To address this issue, we use [epsg.io](http://epsg.io/)'s free API to obtain coordinates with higher precision ([API description](https://github.com/klokantech/epsg.io)). We wrote a function that converts a series of locations from one projection system to the other for this task.

### Sidewalk Block Partition

Most of the sidewalk blocks are too long to be included in single image, hence we may want to separate single block into multiple partitions of similar length, then retrieve these images separately. So the next thing to do is to know about how many photos should be taken along the sidewalk to cover the whole area, along with location of each partitioned block. We desinged an algorithm to approximate a simpler shape of the sidewalk, then do partition on the simplified shape to obtain requried partitions.

The approximation algorithm is based on the assumpiton that most of the blocks are neary rectangular-shaped. Firstable, we approxmiate the block as a quadrilateral defined by points which obtain extreme value (maximum and minimum) on both coordinate directions of the shape polygon. Then, take the longest side of the quadrilateral to decide number of partitions and main heading direction of the block. Finally we partitioned the longest edge along with the edge across the quadrilateral, and take the midpoint of evenly segmented points on both sides as partition's center.

### Street Matching and Camera Settings

The main problem of the dataset is that there's no information about which road it belongs in the sidewalk dataset. Also, we need to know relative position between street and sidewalk to make sure the camera is set up on the correct side of target sidewalk so as to obtain valid result. In spatial database applications, the most basic way for various kinds of searching operations (e.g., intersection and nearest-neighbor search) is to build up index for regtangualr bounding boxes of all itmes, then work on relationship between bounding boxes before diving into analysis on detailed shapes inside. Another useful clue that can be applied to match between street segment and sidewalk is using angle difference between heading directions, since idealy they're nearly parallel to each other.

So this is how we deal with this case. First, we build up an R-tree index for all line segments in the street dataset, then use the center of target sidewalk partition to do nearest-neighbor query (on bounding boxes) for possible candidates, then use angle differenceto find out segment that best fits.

### Obtaining Sidewalk Images from Google's Street View API

Other than solving camera heading, we need to decide other factors such as camera position, pitch rotation, and zooming for querying street view images, while guaranteering the target to be fetched has proper size or portion in the image. However, obtaining the right camera settings is another researchable problem far beyond our main goal, so we just set all camera positions to be some point away from partition centner at a fixed distance, and use default value in Google's API for other settings.

### Future Work

We're told that the original datset for sidewalks [Link](https://data.boston.gov/dataset/sidewalk-inventory) has more attributes that are crucial to refine all above tasks, such as street belonging and sidewalk width. Future updates will combine this dataset so that we can obtain more accurate camera position and settings.

Also, the assumptions we used for generating camera settings can fail in some cases, and there are still lots of possible improvement can be done in the future, like approximating parameters other than position and heading for the query. 

### Dependencies

All the programs are developed under Python3.7, and requre these external libraries other than built-ins:

* `requests`, library for HTTP requests
* `pyshp`, library for reading Shapefile
* `rtree`, wrapper library for [libspatialindex](https://libspatialindex.org/) to build up R-tree index.
* `nvector`, library that provides tools for solving common geographical questions
* `geopy`, library for geocoding and distance computation
* `PyGeodesy`, library for geodesy operations

First, run this command to install all dependencies:

```
>> python3.7 -m pip install -r dependencies.txt
```

Then follow [this](http://toblerity.org/rtree/install.html) instruction to have `libspatialindex` installed. For macOS users (which is not covered from official website), run `brew install spatialindex` through `homebrew` to install this package.

### How to run
#### Coordination Conversion

Say you have your Shapefiles for street and sidewalk in directories `ST_DB` and `SW_DB`, and want to output the converted result to `ST_OUT_PATH`, `SW_OUT_PATH`, respectively. Then you can run this command to convert both datasets:
```
>> python3.7 dataset_convert.py "ST_DB" "SW_DB" "ST_OUT_PATH" "SW_OUT_PATH"
```

#### Partitioning, Query Generation and Obtain Images

To partition converted sidewalk datset and generate query parameters, use `query_generation.py` and run:

```
>> python3.7 query_generation.py [YOUR_PARAMETERS...]
```

For details about parameters, check them out by running:

```
>> python3.7 query_generation.py -h
```

Running `query_generation` will output three text files:
- `sidewalk_info.txt`: Information of sidewalk blocks, mainly about how many partitions are made for this block for querying.
- `metadata.txt`: Metadata for partition queries, includeing their center position, heading direction and the matched street segment.
- `queries.txt`: Query parameters for Google street view API (in JSON string format)

As for obtaining sidewalk from queries generated, unfortunately we don't have a proper solution to retrieve images for now. Since Google's street view API is a chraged service, user may consider not requesting all images at once, just make a random-sampled subset to reduce cost, or need checkpoint/cache record to enable bulk task and to avoid retrieving the same image twice.

However, if you'd like to sample from the set of all queries randomly, you can try `sample_retrive.py` and `query_sampling.py`, which samples from output result above, filter out ones with valid result from Google's API, and query street view images from these samples.

Google's API requires product key and signature secret for forming queries, to separate credential information, all scripts that call street view API require users to store credentials in a JSON file with this format:

```json
{
  "key": "[Your Google API key here]",
  "secret": "[And your API signature secret here]"
}
```

Suppose you store all outputs from `query_generation` under `partitions` directory, and store the keys in `credentials.json`. Then running the following commands will randomly select 100 valid queries (out of 1000 samples) and store images obtained to `sample_output` directory (with *test_sample_* as filename prefix): 

```
>> python3.7 query_sampling.py partitions/queries.txt partitions/metadata.txt 100 credentials.json partitions/samples.txt 1000
...(some output)...
>> python3.7 sample_retrive.py partitions/samples.txt credentials.json sample_output test_sample_ -v
...
```

