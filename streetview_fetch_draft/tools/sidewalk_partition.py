""" Sidewalk_Partition.py

    Author: Po-Yu Hsieh (pyhsieh@bu.edu)
    Last Update: 2019/05/01
"""

import math
import os.path
import json
import csv
from itertools import islice
import numpy as np
from rtree import index
import nvector as nv
from geopy.distance import geodesic
from pygeodesy.formy import bearing

class SidewalkQueryToolkit():
    """ Toolkit for required computation for this module.
    """
    __wgs84 = nv.FrameE(name='WGS84')

    def __init__(self):
        pass

    #################################
    # nvector library related
    #################################
    @classmethod
    def distance_to_line(cls, p0, p1, p2, latlong=True):
        """ Compute nearest distance between point p0 and line defined by
            points (p1, p2).

            Args:
                p0, p1 p2 - (tuple[2](float)) Coordinates
                latlong - True for lat-long system

            Return:
                (float) distance in meters
        """
        if latlong:
            idx_lat, idx_long = 0, 1
        else:
            idx_lat, idx_long = 1, 0

        # If p1 == p2, then just point distance
        p1a, p2a = np.asarray(p1), np.asarray(p2)
        if np.allclose(p1a, p2a):
            return cls.compute_coordinate_distance(p0, p1, latlong)

        # Build up sphere line and compute distance
        point1 = cls.__wgs84.GeoPoint(p1[idx_lat], p1[idx_long], degrees=True)
        point2 = cls.__wgs84.GeoPoint(p2[idx_lat], p2[idx_long], degrees=True)
        point0 = cls.__wgs84.GeoPoint(p0[idx_lat], p0[idx_long], degrees=True)
        path_line = nv.GeoPath(point1, point2)

        return path_line.cross_track_distance(point0).ravel()

    @classmethod
    def nearest_point_on_line(cls, p0, p1, p2, lat_long=True):
        """ Compute nearest point on line defined by points (p1, p2)
            from point p0

            Args:
                p0, p1, p2 - (tuple[2](float)) Coordinates.
                lat_long - (bool) Whether it's lat-long system

            Return:
                (tuple[2](float)) Lat-long coordinate of nearest point.
        """
        if lat_long:
            idx_lat, idx_long = 0, 1
        else:
            idx_lat, idx_long = 1, 0

        point1 = cls.__wgs84.GeoPoint(p1[idx_lat], p1[idx_long], degrees=True)
        point2 = cls.__wgs84.GeoPoint(p2[idx_lat], p2[idx_long], degrees=True)
        point0 = cls.__wgs84.GeoPoint(p0[idx_lat], p0[idx_long], degrees=True)
        path_line = nv.GeoPath(point1, point2)
        result = path_line.closest_point_on_great_circle(point0).latlon_deg

        return (result[0][0], result[1][0])

    @classmethod
    def get_outreach(cls, start, direction, distance, lat_long=True):
        """ Wrapper for nvector's displace() function.

            Args:
                start - (tuple[2](float)) Start position
                direction - (float) 360-compass outreach direction
                distance - (float) Distance (in meters) from the start point
                lat_long - (bool) Whether lat-long system is used for point

            Return:
                (tuple[2](float)) Lat-long coordinate of outreach destination.
        """

        if lat_long:
            idx_lat, idx_long = 0, 1
        else:
            idx_lat, idx_long = 1, 0

        point_s = cls.__wgs84.GeoPoint(start[idx_lat], start[idx_long], degrees=True)
        dest, _ = point_s.displace(distance=distance, azimuth=direction, degrees=True)
        return dest.latitude_deg, dest.longitude_deg


    #################################
    # geopy/pygeodesy related
    #################################
    @staticmethod
    def compute_coordinate_distance(p1, p2, lat_long=True):
        """ Compute distance between two global coordinate points.

            Return:
                (float) Distance by meters.
        """
        p1_p, p2_p = (p1, p2) if lat_long else ((p1[1], p1[0]), (p2[1], p2[0]))
        return geodesic(p1_p, p2_p).meters

    @staticmethod
    def approx_quadrilateral(pts, xy_coordinate=True):
        """ Approximate quadrilateral shape of a polygon.

            Args:
                pts: list(tuple[2](float)) Polygon points
                xy_coordinate: Whether x-y/lon-lat system is used.

            Return:
                (list[4](tuple[2](floats)))
                        X-Y points for quadrilateral approximation.
        """
        if type(pts) != list or len(pts) < 3:
            return None
        # Format data to numpy structure. Swap columns if needed
        data_arr = np.array(pts)
        if not xy_coordinate:
            data_arr[:, [0, 1]] = data_arr[:, [1, 0]]
        # Find bounding box index for each column
        # This assumes that most of the blocks have shape similar rectangal, but not all the cases
        p_idx_min_x, p_idx_min_y = data_arr.argmin(axis=0)
        p_idx_max_x, p_idx_max_y = data_arr.argmax(axis=0)

        # Get approximated corners from points obtaining extreme values
        return data_arr[p_idx_max_x], data_arr[p_idx_max_y], \
                data_arr[p_idx_min_x], data_arr[p_idx_min_y]

    @staticmethod
    def get_angels(p1, p2, yx_cord=True):
        """ Compute heading/counter-heading from p1 to p2.
            Note: The actual heading at p1 and p2 are different on
            bearings(). We use p1's bearing as result.

            Args:
                p1 - tuple[2](float) Start point.
                p2 - tuple[2](float) End point.
                yx_cord - (bool) whether the coordination is Y-X system
            Return: (float) heading direction, (float) inverse heading
                    Note: compass-360. north=0, east=90, etc.
        """
        if yx_cord:
            xs, ys = ((p1[1], p2[1]), (p1[0], p2[0]))
        else:
            xs, ys = ((p1[0], p2[0]), (p1[1], p2[1]))

        angle = bearing(ys[0], xs[0], ys[1], xs[1])

        if angle <= 180.0:
            bearings = (angle, angle + 180.0)
        else:
            bearings = (angle, angle - 180.0)
        return bearings

    @classmethod
    def partition_with_direction_line(cls, line, part_length, dist_f=None,
                                 xy_coordinate=True):
        """ Partition a line segment into pieces, and provide approximated center and direction.

            Args:
                line - (list[2](tuple[2](float))) Line segment where camera should be set along with.
                (for the rest of them, just see below)
        """
        if not dist_f:
            dist_f = cls.compute_coordinate_distance

        # This is required for applying geo-distance functions, where Y/X system
        # is used in general
        if xy_coordinate:
            line_yx = [np.array([y, x]) for (x, y) in line]
        else:
            line_yx = line

        line_length = dist_f(line_yx[0], line_yx[1])

        # First compute how may partitions to be generated, then do 'cyclic partition'
        # to find out center of each partition.
        # For instance, to compute 10 centers between evenly partitioned [0, 10]:
        # s = linspace(0, 10, 10*2, endpoint=False) // [0, 0.5, 1, ..., 9.5] (20)
        # s[1::2]                                   // [0.5, 1.5, ..., 9.5]  (10)
        # TODO: Does general geo-library support this functionality to increase precision?
        partition_size = math.ceil(line_length / float(part_length))
        partitions = np.linspace(line[0], line[1], partition_size * 2, endpoint=False)[1::2]
        # For simplicity, make it be tuple
        partition_centers = [tuple(cent) for cent in partitions]

        return partition_centers, cls.get_angels(line[0], line[1], not xy_coordinate)

    @classmethod
    def partition_with_direction(cls, quad, part_length, dist_f=None,
                                 xy_coordinate=True):
        """ Partition a quadrilateral into pieces, and provide approximated center and direction.

            Args:
                quad - (list[4](tuple[2](float))) Quadrilateral points for sidewalk block.
                part_length - (float) Partition length (in meters).
                dist_f - (function(p1: tuple[2](float), p2: tuple[2](float)))
                        Distance function given two lat-long coordinates.
                xy_coordinate - (bool) Whether input is in x-y, or long-lat system.
        """
        if not dist_f:
            dist_f = cls.compute_coordinate_distance

        # Step 1: Find the longest side as reference
        line_points_ref = [(0, 1), (1, 2), (2, 3), (3, 0)]

        # This is required for applying geo-distance functions, where Y/X system
        # is used in general
        if xy_coordinate:
            quad_yx = [np.array([y, x]) for (x, y) in quad]
        else:
            quad_yx = quad

        side_lengths = [dist_f(quad_yx[i1], quad_yx[i2]) for i1, i2 in line_points_ref]
        ref_side_1_idx = np.argmax(side_lengths)
        ref_side_1 = line_points_ref[ref_side_1_idx]

        # Step 2: Obtain the accrossed side (the 2-next in cyclic index)
        start_1, end_1 = quad[ref_side_1[0]], quad[ref_side_1[1]]
        ref_side_2_idx = (ref_side_1_idx + 2) % 4
        ref_side_2 = line_points_ref[ref_side_2_idx]
        start_2, end_2 = quad[ref_side_2[1]], quad[ref_side_2[0]] # Adjust opposite direction

        # Step 3: Compute partition "semi-center"s and find the midpoint
        # First compute how may partitions to be generated, then do 'cyclic partition'
        # to find out center of each partition.
        # For instance, to compute 10 centers between evenly partitioned [0, 10]:
        # s = linspace(0, 10, 10*2, endpoint=False) // [0, 0.5, 1, ..., 9.5] (20)
        # s[1::2]                                   // [0.5, 1.5, ..., 9.5]  (10)
        # TODO: Does general geo-library support this functionality to increase precision?
        partition_size = math.ceil(side_lengths[ref_side_1_idx] / float(part_length))
        partitions_1 = np.linspace(start_1, end_1, partition_size * 2, endpoint=False)[1::2]
        partitions_2 = np.linspace(start_2, end_2, partition_size * 2, endpoint=False)[1::2]
        # For simplicity, make it be tuple
        partition_centers = [tuple(np.mean([seg_cen_1, seg_cen_2], axis=0))
                             for (seg_cen_1, seg_cen_2) in zip(partitions_1, partitions_2)]

        return partition_centers, cls.get_angels(start_1, end_1, not xy_coordinate)

    # R-tree index related
    @classmethod
    def build_geodb(cls, path_streetjson, filename, overwrite=True):
        """ Build up a R-Tree based geodb of street segments.

            Args:
                path_streetjson - (str) Path to street db json file
                filename - (str) filename used to store R-tree index
                overwrite - (bool) whether to overwrite existing file
                        Note: rtree does not support read-only mode.
        """
        idx_p = index.Property()
        idx_p.overwrite = overwrite
        idx = index.Index(filename, properties=idx_p)
        with open(path_streetjson, "r") as fd_r:
            for line in fd_r.readlines():
                street_data = json.loads(line)
                points = street_data["points"]
                # Note: X(long)-Y(lat) coordinates
                db_idx = 0
                for seg_id, (start_pt, end_pt) in enumerate(zip(points, islice(points, 1, None))):
                    bbox = ( # left, bottom, right, top
                        min(start_pt[0], end_pt[0]), min(start_pt[1], end_pt[1]),
                        max(start_pt[0], end_pt[0]), max(start_pt[1], end_pt[1])
                    )
                    headings = cls.get_angels(start_pt, end_pt, False)
                    db_data = {"st_name": street_data["name"],
                               "segment_id": seg_id,
                               "segment_points": (start_pt, end_pt),
                               "headings": headings}
                    idx.insert(db_idx, bbox, obj=db_data)
                    db_idx += 1
        return idx

    @staticmethod
    def read_geodb(filename):
        """ Simple wrapper to read existing R-tree index file.
        """
        pt = index.Property()
        pt.overwrite = False
        return index.Index(filename, properties=pt)

    @classmethod
    def generate_sidewalk_queries(cls, target_center, target_slope, street_idx, threshold=8.0,
                                  shot_angle=30.0, shot_dist=10.0):
        """ Return a list of Google Street View API queries, given
            street and index data.

            Args:
                target_center - (float, float) [X-lon, Y-lat] coordinate
                target_slope = Target direction in 360-degree unit
                street_idx - (rtree.index.Index) Street index db
                threshold - (float) Degree threshold for selecting nearest road segment
                shot_angle - (float) Narrow angle between camera heading and target direction
                shot_dist - (float) Distance between camera and target

            Returns:
                query_params_1 #
                query_params_2 - (dict) Query parameters for street view API
                query_info - (dict) Additional information other than query parameters
        """
        # Step 0: Tune slope
        if target_slope > 180.0:
            target_slope -= 180.0

        # Step 1: Return nearest candidates
        nn_result = list(street_idx.nearest(target_center, 20, objects="raw"))
        # Step 2: Choose the first one that passes threshold.
        #         Otherwise, select the one with lowest angle
        belong_st = None
        min_angle = 180.0
        min_cand = None
        for cand in nn_result:
            angle_diff = abs(min(cand["headings"]) - target_slope)
            if angle_diff <= threshold:
                belong_st = cand
                break
            if angle_diff < min_angle:
                min_angle, min_cand = angle_diff, cand
        if not belong_st:
            belong_st = min_cand
        # Step 3: Identify relative position between road and sidewalk
        #         Use the relative position between direction facing road from sidewalk,
        #         and sidewalk direction to decide walkout direction for camera positioning,
        #         along with camera heading (reverse of walkout direction).
        nearest_proj = cls.nearest_point_on_line(
            target_center, belong_st["segment_points"][0], belong_st["segment_points"][1])
        dir_facing_road = cls.get_angels(target_center, nearest_proj)[0]
        if target_slope <= dir_facing_road <= (target_slope + 180):
            # Road's on clockwise side
            walkout_dir1 = target_slope + shot_angle
            walkout_dir2 = target_slope + 180.0 - shot_angle
        else:
            # Road's on counter-clockwise side
            walkout_dir1 = target_slope + (360.0 if target_slope < shot_angle else 0.0) - shot_angle
            walkout_dir2 = target_slope + 180.0 + shot_angle - \
                    (360.0 if target_slope + shot_angle > 180.0 else 0.0)

        shot_loc_1 = cls.get_outreach(target_center, walkout_dir1, shot_dist)
        shot_loc_2 = cls.get_outreach(target_center, walkout_dir2, shot_dist)

        # Step 4: Reverse walkout direction to obtain camera heading.
        shot_heading_1 = walkout_dir1 + 180.0
        shot_heading_2 = walkout_dir2 + 180.0
        shot_heading_1 -= (360.0 if shot_heading_1 >= 360.0 else 0.0)
        shot_heading_2 -= (360.0 if shot_heading_2 >= 360.0 else 0.0)

        # Step 5: Output camera parameters and other info
        query_params_1 = {
            "location": shot_loc_1,
            "heading": shot_heading_1
        }
        query_params_2 = {
            "location": shot_loc_2,
            "heading": shot_heading_2
        }
        query_info = {
            "st_name": belong_st["st_name"],
            "segment_id": belong_st["segment_id"]
        }

        return query_params_1, query_params_2, query_info

class QueryGenerationRunner():
    """ Wrapped routine for generating streetview panorama queries.
    """

    __meta_headers = ["Sidewalk_Index", "Partition_Index", "Query_ID", "Center_Lon",
                      "Center_Lat", "Street_Belonging", "Street_Segment_Id", "Pano_Location_Lon",
                      "Pano_Location_Lat", "Pano_Heading"]

    def __init__(self, sidewalk_file, index_path, out_path, street_file=None, part_len=20.0, 
                 threshold=8.0, shot_angle=30.0, shot_dist=10.0, verbose=False):
        """
            Args:
                sidewalk_file - (str) File path to sidewalk JSON dataset
                index_path - (str) File path to store disk street index
                out_path - (str) Folder path to store result queries and metadata
                street_file (optional) - (str) File path to street JSON dataset
        """

        self.__tlkt = SidewalkQueryToolkit
        self.sidewalk_file = sidewalk_file

        if street_file:
            self.st_index = self.__tlkt.build_geodb(street_file, index_path, True)
        else:
            self.st_index = self.__tlkt.read_geodb(index_path)
        self.out_path = out_path
        self.part_len = part_len
        self.threshold = threshold
        self.shot_angle = shot_angle
        self.shot_dist = shot_dist
        self.verbose = verbose

    def run(self):
        """ Run query-param generation algorithm, and write metadata and query params to files.
        """
        tool = self.__tlkt
        meta = []
        queries = []
        sidewalk_info = []
        # Go through all side walk blocks to do partitioning, and decide camera
        # settings for each partition.
        with open(self.sidewalk_file, "r") as fd_r:
            for sw_idx, line in enumerate(fd_r.readlines()):
                sw_row = json.loads(line)
                sw_points = sw_row["points"]
                quad = tool.approx_quadrilateral(sw_points)
                if not quad:
                    continue
                partitions, (ang_1, ang_2) = tool.partition_with_direction(
                    quad, self.part_len)
                minor_ang = min(ang_1, ang_2)
                sidewalk_info.append({
                    "sidewalk_index": sw_idx, "quad_points": [list(d) for d in quad],
                    "num_partitions": len(partitions), "direction": minor_ang
                })
                for pt_idx, partition in enumerate(partitions):
                    q_params_1, q_params_2, q_info = tool.generate_sidewalk_queries(
                        partition, minor_ang, self.st_index, self.threshold,
                        self.shot_angle, self.shot_dist)
                    for qd_idx, param in enumerate([q_params_1, q_params_2], 1):
                        queries.append(param)
                        metadata = (sw_idx, pt_idx, qd_idx, partition[0], partition[1],
                                    q_info["st_name"], q_info["segment_id"],
                                    param["location"][0], param["location"][1],
                                    param["heading"])
                        if self.verbose:
                            print("Result: {}".format(metadata))
                        meta.append(metadata)

        # Write out to text files
        with open(os.path.join(self.out_path, "queries.txt"), "w") as fd_wq:
            for query in queries:
                fd_wq.write("{}\n".format(json.dumps(query)))

        with open(os.path.join(self.out_path, "sidewalk_info.txt"), "w") as fd_ws:
            for info in sidewalk_info:
                fd_ws.write("{}\n".format(json.dumps(info)))

        with open(os.path.join(self.out_path, "metadata.txt"), "w") as fd_wm:
            wtr = csv.writer(fd_wm, delimiter=',')
            wtr.writerow(self.__meta_headers)
            wtr.writerows(meta)
