# Sidewalk Dataset Preprocessing

In this document we'll describe how we preprocess dataset we're given, and derive what we needed for querying Google's [street view API](https://developers.google.com/maps/documentation/streetview/intro) for sidewalk images.

## About Dataset and Resource

We got our sidewalk and street data from Boston Hack 2018's dataset. The whole dataset can be obtained from project description [here](https://docs.google.com/document/d/1jS3QsgjQLZyYoZzs0WbrA_SrOWAhEUv6Cc_a8X0oHJA/).

The street dataset consists of line segments of streets in Boston; and sidewalk contains shape polygons of planned sidewalk blocks. Both datasets are using coordinates with *EPSG:6492* ([descriptions](https://epsg.io/6492)) projection settings. 

### Coordinate Conversion

Since Google's API only accept *WGS84* (worldwide coordinate system, [Ref](https://en.wikipedia.org/wiki/World_Geodetic_System)), while the original dataset use another coordinate system, we need to transform location coordinates beforehand. There are several Python libraries that supports coordinate conversion, such as `pyproj`. However, we found that result from local machine suffers from significant numeral error, which can't be directly applied in later tasks.

To address this issue, we use [epsg.io](http://epsg.io/)'s free API to obtain coordinates with higher precision [here](https://github.com/klokantech/epsg.io). We wrote a function that can convert a series of locations from one projection system to the other.

### Sidewalk Block Partition

Most of the sidewalk blocks are too long to be included in single image, hence we need to separate them into several partitions, then obtain their images separately. So the next thing to do is to know about how many photos to be taken along the sidewalk, and position of each partition. We desinged an algorithm to approximate a simpler shape of the sidewalk, and do partition on that shape to obtain requried positions.

The approximation algorithm is very simple, and based on the assumpiton that most of the blocks are neary rectangular-shaped. Firstable, the quadrilateral block is defined by points that obtained the extreme value (maximum and minimum) on both coordinate directions. Then, take the longest side of the quadrilateral to decide number of partitions and main heading direction to the block. Last we partitioned the longest edge along with the edge across, and take the midpoint of points on both sides as partition's center.

### Street Matching and Camera Settings

A problem of the dataset is that the sidewalk dataset doesn't provide any information about which road it belongs to. Also, we need to know relative position between street and sidewalk to make sure the camera is set up on the correct side of the sidewalk and obtain valid result. In spatial database, the basic way for various kinds of searching is to build up index for regtangualr bounding boxes of all the itmes, and work on relationship of bounding boxes before analyze the more detailed shapes inside. Another useful clue that can be used to match street and sidewalk is using angle difference between their heading directions, since idealy they're nearly parallel in directions.

So this is how we deal with this case. First, we build up an R-tree index for bounding boxes of all line segments in the street dataset, then use the center of sidewalk partition to do nearest-neighbor query for possible candidates, then use angle difference with block direction to find out the segment that best fits.

### Obtaining Sidewalk Images from Google's Street View API

Other than solving camera heading, we need to decide other factors such as camera position, pitch rotation, and zooming for querying street view images, while guarantee the area we want appears is large enough on result image. However, obtaining the right camera settings is another researchable problem far beyond our goal, so we just set all camera positions to be away from partition centner at a fixed distance, and use default value in Google's API for other settings.

### Future Work

We're told that the original datset for sidewalks [Link](https://data.boston.gov/dataset/sidewalk-inventory) includes more attributes that are crucial to refine above tasks, such as street it belongs to and sidewalk width. Further update will combine this dataset and obtain more accurate.

Also, the assumptions we used for generating camera settings can fail in some cases, and there are still lots of possible improvement can be done in the future, such as approximating other parameters for the query. 

### Dependencies

All the programs are developed under Python3.7, and requre these external libraries other than built-ins:

* `requests`, library for HTTP requests
* `pyshp`, library for reading Shapefile
* `rtree`, wrapper library for [libspatialindex](https://libspatialindex.org/) to build up R-tree index.
* `nvector`, library that provides tools for solving common geographical questions
* `geopy`, library for geocoding and distance computation
* `PyGeodesy`, library for geodesy operations

Running `python3.7 pip install dependencies.txt` will install above libraries, then follow [this](http://toblerity.org/rtree/install.html) instruction to have `libspatialindex` installed. For macOS users, run `brew install spatialindex` through `homebrew` will install this package.

### How to run
#### Coordination Conversion

Say you have your Shapefiles for street and sidewalk in directories `ST_DB` and `SW_DB`, and want to output the converted result to `ST_OUT_PATH`, `SW_OUT_PATH`, respectively. Then you can run this command to convert both datasets:
```
python3 dataset_convert.py "ST_DB" "SW_DB" "ST_OUT_PATH" "SW_OUT_PATH"
```

#### Partitioning, Query Generation and Obtain Images

To partition converted sidewalk datset and generate query parameters, use `query_generation.py` and run:

```
python3.7 query_generation.py [YOUR_PARAMETERS...]
```

For details about parameters, check them out by running:

```
python3.7 query_generation.py -h
```

Running `query_generation` will output three text files:
- `sidewalk_info.txt`: Information of sidewalk blocks, mainly about how many partitions are made for this block for querying.
- `metadata.txt`: Metadata for partition queries, includeing their center position, heading direction and the matched street segment.
- `queries.txt`: Query parameters for Google street view API (in JSON string format)

