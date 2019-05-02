""" sample_retrive.py

    Author: Po-Yu Hsieh (pyhsieh@bu.edu)
    Last Update: 2019/05/02
"""

import os, sys
import json
import tools.streetview_retrieval as sr

def fetch_sidewalk_images(query_file, auth_path, output_path, tag, verbosity=False):
    """ Obtain images from sample information provided in run.py.

        Args:
            query_file - (str) File path for query information.
            auth_path - (str) File path for Google API's auth keys.
            out_path - (str) Output path for returned images.
            tag - (str) Prefix for output images
            verbosity - (bool) Verbosity settings for StreetviewQueryToolset
    """
    qrtool = sr.StreetviewQueryToolset(credential_path=auth_path, verbosity=verbosity)
    with open(query_file, "r") as fd_r:
        for line in fd_r.readlines():
            query_params = json.loads(line)["query"]
            # Even if it's Google we can still get errors, in this case we just retry it.
            while True:
                try:
                    qrtool.get_streetview(output_path, json.loads(line)["query"], tag, False)
                except:
                    continue
                else:
                    break

def run():
    if len(sys.argv) < 5 or (len(sys.argv) == 6 and "-v" not in sys.argv):
        print("Usage:\n  python3.7 sample_retrive.py QUERY_PATH AUTH_PATH OUT_PATH FILE_PREFIX [-v]")
        return
    arguments = [i for i in sys.argv[1:]]
    if len(argument) == 5:
        _ = argument.pop(argument.index("-v"))
        verbosity = True
    else:
        verbosity = False
    query_file, auth_path, out_path, tag = arguments
    fetch_sidewalk_images(query_file, auth_path, out_path, tag, verbosity)


if __name__ == "__main__":
    run()
