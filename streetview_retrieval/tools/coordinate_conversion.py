""" coordinate_conversion.py

    Author: Po-Yu Hsieh (pyhsieh@bu.edu)
    Last update: 2019/05/01

    Simple coordinate transform on Shapefile datasetwith the help of MapTiler's API

    Reference:
        Official Website: http://epsg.io/
        GitHub Repo:      https://github.com/klokantech/epsg.io
"""
import json
from time import sleep
import requests
import shapefile

class CoordinateConversionToolset():
    """ Simple toolkit for onverting shape data of a Shapefile dataset.
    """

    _URL_CONVERSION = "https://epsg.io/trans"
    _BULK_SIZE = 90

    def __init__(self, input_file, output_file, source_code, target_code, xy_coordinate, record_map=None):
        """ Initialize conversion settings.

            Args:
                input_file: (str) Shapefile dataset for input coordinates.
                output_file: (str) Path to output text file.
                source_code: (str) Projection system used by input data.
                target_code: (str) Projection system to be output.
                xy_coordinate: (bool) Whether input is of X-Y/Lon-Lat format.
                record_map: (function(dict->dict)) function used to extract
                    additional information from Shapefile record, which will
                    be updated to JSON string of row data. 
        """
        self.input_file = input_file
        self.output_file = output_file
        self.source_code = source_code
        self.target_code = target_code
        self.xy_sys = xy_coordinate
        self.rec_map = record_map

    def query_points(self, points, xy_coordinate=True):
        """ Obtain converted coordinates.

            Args:
                points - (list(tuple[2](float))) List of coordinates to be converted.
                xy_coordinate - (bool) Whether input is of X-Y/Lon-Lat format

            Return:
                (list(tuple[2](flo at))) List of converted result, with the same coordinate order
        """
        x_idx, y_idx = (0, 1) if xy_coordinate else (1, 0)
        params = {"s_srs": self.source_code, "t_srs": self.target_code}
        result = []
        data_size = len(points)
        bulk_start, bulk_end = 0, 0
        while bulk_end < data_size:
            bulk_start, bulk_end = bulk_end, bulk_end + self._BULK_SIZE
            bulk_points = points[bulk_start:bulk_end]
            query_data = ";".join(["{0:f},{1:f}".format(point[x_idx], point[y_idx]) for point in bulk_points])
            params["data"] = query_data
            respond = requests.get(url=self._URL_CONVERSION, params=params)
            r_json = respond.json()
            if xy_coordinate:
                result.extend([float(loc_obj["x"]), float(loc_obj["y"])] for loc_obj in r_json)
            else:
                result.extend([float(loc_obj["y"]), float(loc_obj["x"])] for loc_obj in r_json)
        return result

    def convert_shape_coordinates(self):
        """ Simple converter for coordination conversion.

            Args:
                xy_coordinate - (bool) Whether input is of X-Y/Lon-Lat format
        """
        with shapefile.Reader(self.input_file) as s_file, open(self.output_file, "w") as fd_w:
            for row_s, row_r in zip(s_file.shapes(), s_file.records()):
                # Gather several rows into a bulk
                row_points = row_s.points
                converted_points = self.query_points(row_points, self.xy_sys)
                out_data_row = {"points": converted_points}
                if self.rec_map:
                    out_data_row.update(self.rec_map(row_r))
                write_content = json.dumps(out_data_row)
                fd_w.write(write_content + "\n")
                sleep(0.08)

"""
_DB_PATH = "../Dataset/Boston_Hacks_Shared_Folder/Streets/Streets.shp"
_OUT_PATH = "./Streets_poly_converted.txt"
_SOURCE_CO_CODE = 6492
_TARGET_CO_CODE = 4326
"""
