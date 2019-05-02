""" query_sampling.py

    Author: Po-Yu Hsieh (pyhsieh@bu.edu)
    Last Update: 2019/05/02
"""

import os
import sys
import json
import csv
from random import randint, sample
from copy import deepcopy
import tools.streetview_retrieval as sr


def query_count(filepath):
    with open(filepath, "r") as fd_r:
        result = len(fd_r.readlines())
    return result

def sample_runner(file_queries, file_meta, sample_size, credential_path, output_info=None, subsample=None):
    print("Initialize search tool...")
    qrtool = sr.StreetviewQueryToolset(credential_path=credential_path, verbose=True)
    query_data_m = {
        "location": "",
        "size": "640x420",
        "heading": 0,
        "fov": 90,
        "pitch": 0,
        "radius": 20,
        "source": "outdoor"
    }
    query_data_s = {
        "pano": "",
        "size": "640x420",
        "heading": 0,
        "fov": 90,
        "pitch": 0,
        "radius": 20,
        "source": "outdoor"
    }

    k = sample_size
    if subsample and subsample > k:
        sample_list = sample(range(query_count(file_queries)), subsample)
        subsample = True
    else:
        subsample = False

    buckets = [None for i in range(k)]
    stream_ct = 0

    print("Sampling...")
    with open(file_meta, newline='') as meta_csv, open(file_queries) as query_file:
        m_reader = csv.DictReader(meta_csv)
        for row_id, (m_dict, q_line) in enumerate(zip(m_reader, query_file.readlines())):
            # Step 0: Work under subsampling
            if subsample and (row_id not in sample_list):
                continue
            # Step 1: Form parameters and check data availability
            print("Handling data id: {}".format(row_id))
            query_json = json.loads(q_line)
            query_data_m["location"] = "{0:f},{1:f}".format(*(query_json["location"][::-1]))
            query_data_m["heading"] = query_json["heading"]
            pano_id = qrtool.get_meta(query_data_m)

            if pano_id:
                query_data_s["pano"] = pano_id
                query_data_s["heading"] = query_json["heading"]
                # Step 2-1: For the first k ones, insert them anyway
                if stream_ct < k:
                    buckets[stream_ct] = {"row_id": row_id, "meta": m_dict, "query": deepcopy(query_data_s)}
                # Step 2-2: For items afterward, do resevoir sampling
                else:
                    rv_decision = randint(0, stream_ct)
                    if rv_decision < k:
                        buckets[rv_decision] = {"row_id": row_id, "meta": m_dict, "query": deepcopy(query_data_s)}
                # Increment counter
                stream_ct += 1

        # Step 3: Make queries based on sampled result
        print("Query based on sample result...")
        # For safety.
        if output_info:
            fd_w = open(output_info, "w")
            for q_item in buckets:
                fd_w.write("{}\n".format(json.dumps(q_item)))
            fd_w.close()
        print("Done!")

def run():
    if not 5 <= len(sys.argv) <= 6:
        print("Usage: python3.7 query_sampling.py QUERY_FILE META_FILE SAMPLE_SIZE AUTH_PATH OUTPUT_INFO_PATH ([SUBSAMPLE_SIZE])")
        return
    file_queries, file_meta, sample_size, credential_path, output_info = sys.argv[1:6]
    sample_size = int(sample_size)
    if len(sys.argv) == 6:
        subsample = int(sys.argv[6])
    else:
        subsample = None
    sample_runner(file_queries, file_meta, sample_size, credential_path, output_info, subsample)

if __name__ == "__main__":
    run()
