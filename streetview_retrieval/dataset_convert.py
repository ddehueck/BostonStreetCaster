""" dataset_convert.py
    Author: Po-Yu Hsieh (pyhsieh@bu.edu)
    Last update: 2019/05/02

"""
import sys
import tools.coordinate_conversion as corcv

def run():
    if len(sys.argv) != 5:
        print("Usage: dataset_convert.py [STREETDB_IN] [SIDEWALKDB_IN] [STREETDB_OUT] [SIDEWALKDB_OUT]")
        return

    _STREET_DB_PATH, _SIDEWALK_DB_PATH, _STREET_CONV_OUT_PATH, _SIDEWALK_CONV_OUT_PATH = sys.argv[1:]
    _SRC_CODE, _TGT_CODE = 6492, 4326  # EPSG codes

    _PARAMS_ST = {
        "input_file": _STREET_DB_PATH, "output_file": _STREET_CONV_OUT_PATH,
        "source_code": _SRC_CODE, "target_code": _TGT_CODE, "xy_coordinate": True,
        "record_map": lambda rec: {"name": rec["GREENBOOK"]}
    }

    _PARAMS_SW = {
        "input_file": _SIDEWALK_DB_PATH, "output_file": _SIDEWALK_CONV_OUT_PATH,
        "source_code": _SRC_CODE, "target_code": _TGT_CODE, "xy_coordinate": True
    }

    print("Start converting street dataset coordinates...")
    toolkit = corcv.CoordinateConversionToolset(**_PARAMS_ST)
    toolkit.convert_shape_coordinates()
    print("Start converting sidewalk dataset coordinates...")
    toolkit = corcv.CoordinateConversionToolset(**_PARAMS_SW)
    toolkit.convert_shape_coordinates()
    print("Done!")


if __name__ == "__main__":
    run()
