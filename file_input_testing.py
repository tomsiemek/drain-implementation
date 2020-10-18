from drain import Drain
import time
import sys
import re


def extract_filename(src):
    splitted = src.split("\\")
    return splitted[len(splitted) - 1]

drain = Drain()
filename = ".\\logs\\Hadoop_2k.log" if len(sys.argv) < 2 else sys.argv[1]
input_file = open(filename, "r")
timestr = time.strftime("%Y%m%d-%H%M%S")
output_structured = open(".\\output\\output_" + extract_filename(filename)  + timestr + ".txt", "a")
output_clusters = open(".\\output\\clusters_" + extract_filename(filename)  + timestr + ".txt", "a")
for l in input_file:
    output_structured.write(f"{l} -> {drain.parse_message(l)}\n")
for c in drain.give_cluster_list():
    output_clusters.write(c + "\n")