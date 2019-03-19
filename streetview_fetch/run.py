from time import sleep
from itertools import islice
import streetview_retrieval as sr

_OUTPUT_DIR = ""
_CREDENTIAL_PATH = ""
# _DB_PATH = "../Dataset/Boston_Hacks_Shared_Folder/Streets/Streets.shp"
_DB_PATH = "./Streets_converted.txt"

"""
convert_settings = {
     'proj': 'lcc',          # Projection Method (LCC)
     'pm': 'greenwich',      # Prime Meridian
     'datum': 'NAD83',       # Datum
     'lat_0': 41.0,          # Latitude of origin
     'lat_1': 41.71666667,   # First 
     'lat_2': 42.68333333,   # 
     'lon_0': -71.5,         # Central meridian
     'x_0': 656166.66666667, # False easting
     'y_0': 2460625.0,       # False northing
     'units': "us-ft"        # Units (US Surveyor's Ft.)
    }
"""

parameters = {
    "size": "640x640", "location": "",
    "fov": 90, "source": "outdoor", "heading": 0, "pitch": 30 }

_KEY, _SECRET = sr.get_credentials(_CREDENTIAL_PATH)

DATA_START, DATA_STOP = None, None
for s_points, s_name in islice(zip(*(sr.load_data_converted_json(_DB_PATH))), DATA_START, DATA_STOP):
    # Note: Long-Lat coordinate
    for seg_id, (point_st, point_ed) in enumerate(zip(s_points, s_points[1:]), 1):
        partitions, pitches = sr.segment_partition(point_st, point_ed, False)
        for pos_id, (standpoint_y, standpoint_x) in enumerate(partitions):
            for pitch in pitches:
                tag = "{0:s}_SEG{1:04d}_POS{2:010d}_PIT{3:.3f}_".format(s_name, seg_id, pos_id, pitch)
                print("Position: x={}, y={}".format(standpoint_x, standpoint_y))
                parameters["location"] = "{},{}".format(standpoint_y, standpoint_x)
                parameters["heading"] = pitch
                out_name = sr.get_streetview(_OUTPUT_DIR, _KEY, parameters, _SECRET, tag)
                print("Write to file {}...".format(out_name))
                sleep(0.05)
print("Done!")
