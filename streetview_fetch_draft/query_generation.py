import argparse
import tools.sidewalk_partition as sp

def parse_args():
    parser = argparse.ArgumentParser(description="Sidewalk partition and query parameter \
                                     generation routine for Boston StreetCaster project.")
    """
        Required Arguments
    """
    parser.add_argument("--sidewalkfile", dest="sidewalk_file", type=str, required=True,
                        help="File path to sidewalk JSON dataset.")
    parser.add_argument("--index_path", dest="index_path", type=str, required=True,
                        help="File path to store R-Tree index of street segments.")
    parser.add_argument("--out_path", dest="out_path", type=str, required=True,
                        help="Output folder path to store query parameters and metadata.")

    """
        Optional Arguments
    """
    parser.add_argument("--street_file", dest="street_file", type=str, required=False,
                        help="If R-tree index is not built, then this is the path for converted \
                        street coordinate file used to construct spatial index.")
    parser.add_argument("--part_len", dest="part_len", type=float, required=False,
                        help="Partition lengh for sidewalk blocks (in meters).")
    parser.add_argument("--threshold", dest="threshold", type=float, required=False,
                        help="Threshod for identifying matching street segment (in degrees).")
    parser.add_argument("--shot_angle", dest="shot_angle", type=float, required=False,
                        help="Camera angle difference to sidwalk's direction (in degrees).")
    parser.add_argument("--shot_dist", dest="shot_dist", type=float, required=False,
                        help="Camera distance to sidewalk partition's center (in meters).")
    parser.add_argument("--verbose", dest="verbose", required=False, action="store_true",
                        help="Print out query parameter settings for each partition.")

    return {key: val for key, val in vars(parser.parse_args()).items() if val}

def run():
    """ Main routine.
    """
    arguments = parse_args()
    sp.QueryGenerationRunner(**arguments).run()

if __name__ == "__main__":
    run()
