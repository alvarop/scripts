#!/usr/bin/env python
#
# This script uses ffmpeg to extract frames from video files in a directory
#

import argparse
import os
import subprocess
import sys

parser = argparse.ArgumentParser()


parser.add_argument(
    "--size_limit",
    type=int,
    default=1024 * 1024 * 32,
    help="Ignore files above this size",
)

parser.add_argument(
    "--frame_limit",
    type=int,
    default=256,
    help="Ignore files with more than these many frames",
)

parser.add_argument(
    "--suffix",
    default='"_%04d.png"',
    help="Filename suffix for ffmpeg (file type can be changed here)",
)

parser.add_argument("--output_dir", default="./", help="Place to dump the images")

parser.add_argument("dir", help="Directory to scan")

args = parser.parse_args()

files = []


def get_num_frames(filepath):
    get_frames_cmd = [
        "ffprobe",
        "-v",
        "error",
        "-count_frames",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=nb_read_frames",
        "-of",
        "default=nokey=1:noprint_wrappers=1",
        filepath,
    ]

    result = subprocess.run(get_frames_cmd, stdout=subprocess.PIPE)

    if len(result.stdout.decode("utf-8").strip()) > 0:
        num_frames = int(result.stdout.decode("utf-8").strip().split("\n")[0])
    else:
        num_frames = 0

    return num_frames


def extract_frames(filepath, output_dir, output_format):
    extract_frames_cmd = ["ffmpeg", "-i", filepath, output_dir + "/" + output_format]
    result = subprocess.run(extract_frames_cmd, stdout=subprocess.PIPE)


for filename in sorted(os.listdir(args.dir)):
    filepath = args.dir + "/" + filename
    if (
        os.path.getsize(filepath) < args.size_limit
        and get_num_frames(filepath) < args.frame_limit
    ):
        print("Extracting frames from " + filepath)
        extract_frames(filepath, args.output_dir, filename.split(".")[0] + args.suffix)
