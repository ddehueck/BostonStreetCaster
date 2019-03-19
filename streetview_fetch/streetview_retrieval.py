from os.path import join
import json
import math
from copy import deepcopy
from time import time_ns
from urllib.request import urlretrieve
from sign_url import sign_url
import shapefile
import numpy as np
from pyproj import Proj
from geopy import distance

_URL = "https://maps.googleapis.com/maps/api/streetview?"

def get_credentials(path):
    """ A shorthand function to access google API keys from secret file.

        Args:
            path - (str) Path to credential content (in JSON)

        Returns:
            key - Google API key
            secret - Google API secret
    """
    with open(path, "r") as fd_r:
        content = json.loads(fd_r.read())
    return content["key"], content["secret"]

def segment_partition(p1, p2, lat_long=True):
    """
        Return: list (latitude, longitude), (float) pitch direction
    """
    _PARTITION_UNIT = 15. # Just a rough guess
    steps = int(math.ceil(compute_coordinate_distance(p1, p2, lat_long) / _PARTITION_UNIT))
    # [-180, 180]
    if lat_long:
        xs, ys = ((p1[1], p2[1]), (p1[0], p2[0]))
    else:
        xs, ys = ((p1[0], p2[0]), (p1[1], p2[1]))
    angle = np.rad2deg(np.arctan2(ys[1] - ys[0], xs[1] - xs[0]))
    if angle <= -90: # -180 ~ -90
        pitches = (angle + 270, angle + 450)
    elif angle <= 90: # -90 ~ 90
        pitches = (angle + 90, angle + 270)
    else: # 90 ~ 180
        pitches = (angle - 90, angle + 90)
    segmentations = [cd for cd in zip(np.linspace(ys[0], ys[0], steps)[1:], np.linspace(xs[1], xs[1], steps)[1:])]
    return segmentations, pitches

def compute_coordinate_distance(p1, p2, lat_long=True):
    """
        Note: Lat/Long system

        Returns:
            (float) Distance by meters.
    """
    p1_p, p2_p = (p1, p2) if lat_long else ((p1[1], p1[0]), (p2[1], p2[0]))
    return distance.distance(p1_p, p2_p).m

# TODO: Find out API's query throttling policy
def combine_parameters(param_dict):
    """ Simple URL parameter string generation, does not handle with encoding issues.

        Args:
            param_dict - (dict) Key-value pairs for parameter name and value

        Returns:
            (str) Combined parameter string.
    """
    return "&".join(["{0:s}={1:s}".format(str(k), str(v)) for k, v in  param_dict.items()])

def load_shapedata(path, convert_settings=None):
    """ Load dataset from database and convert to global coordinate system.

        Args:
            path: File path to GIS database file.
            convert_settings: Convert settings sent to pyproj.Proj().

        Returns:
            Conveted database information, represented as a list.
    """
    shapes = []

    # Lon/Lat (or X/Y) to Lon/Lat converter.
    # Note that Google uses Lat/Lon coordinate.
    if convert_settings:
        projector = Proj(convert_settings)
    else:
        projector = lambda x, y: (x, y)

    s_file = shapefile.Reader(path)
    for row in s_file.shapes():
        shapes.append([projector(point[0], point[1], inverse=True) for point in row.points])
    records = [row["GREENBOOK"] for row in s_file.records()]

    s_file.close()
    return shapes, records

def load_data_converted_json(filename):
    """ Get data from line-object json file.

        Args:
            filename - (str) filename
        Returns:
            shapes - (list) List of shape point list.
            records - (list) Label of each data.
    """
    shapes, records = [], []
    for line in open(filename, "r").readlines():
        parsed_json = json.loads(line)
        shapes.append(parsed_json["points"])
        records.append(parsed_json["name"])
    return shapes, records

def get_streetview(output_dir, apikey, settings, secret=None, prefix=""):
    """ Retrive Google street view from given settings.
        Output files will be named of timestamp generated on request.

        Args:
            output_dir - (str) Output directory
            apikey     - (str) Google Map Static API's key value
            secret     - (str) Additional secret key for signature
            settings   - (dict) Key-value pairs for API's parameters
            prefix     - (str) Prefix for output files

        Returns:
            File name of the retrieved image.
    """

    settings_combined = deepcopy(settings)
    settings_combined["key"] = apikey
    url_base = "{0:s}{1:s}".format(_URL, combine_parameters(settings_combined))
    url_retrieval = sign_url(url_base, secret) if secret else url_base
    output_name = "{}{}.jpg".format(prefix, str(time_ns()))
    print("URL request:" + url_retrieval)
    retrive_result = urlretrieve(url_retrieval, join(output_dir, output_name))

    return output_name

def retrieve_streetview_from_dataset(path, convert_settings, retrieve_settings):
    """
        NOTE: Path to database, settings for projection converter, settings for ret-function
        Now restricted to M-Line data
    """
    

    return None
