# coding=utf-8

import argparse
import logging
import time
import os
from spleeter.separator import Separator
#from spleeter.audio.adapter import get_default_audio_adapter

separator = None

def prepare():
    global separator
    separator = Separator('spleeter:2stems', '/Users/lix/Desktop/fasic_cv_sdk/pretrained_models/2stems')

def process(path, out_dir):
    global separator
    # Using custom configuration file.
    # separator = Separator('/path/to/config.json')
    # audio_loader = get_default_audio_adapter()
    # sample_rate = 44100
    # waveform, _ = audio_loader.load(path, sample_rate=sample_rate)
    # with tempfile.TemporaryDirectory() as tmp_dir:
    #     logging.warning("tmp_dir " + tmp_dir);
    #     separator.separate_to_file(path, tmp_dir)
    separator.separate_to_file(path, out_dir, filename_format='{filename}-{instrument}.{codec}')

#logging.basicConfig(level=logging.INFO)
logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%d-%m-%Y:%H:%M:%S', level=logging.INFO)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.description='please enter input file'
    parser.add_argument("-i", "--input", help="input file", dest="input", type=str, default="/Users/lix/Desktop/fasic_cv_sdk/output/")
    parser.add_argument("-o", "--output", help="output dir", dest="output", type=str, default="output/")
    args = parser.parse_args()
    if args.input == "" or args.output == "":
        logging.error("input and output can not be null")
        exit()

    begin_prepare = time.time()
    prepare()
    end_prepare = time.time()
    logging.warning("[time] prepare " + str(end_prepare - begin_prepare))
    logging.info("start spleeter " + args.input + ", out dir " + args.output)

    input_dir = args.input
    output_dir = args.output
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    files = os.listdir(args.input)
    avg_time = 0
    f_n = len(files)
    for file in files:
        if not "wav" in file:
            continue
        file_path = input_dir + "/" + file
        begin_time = time.time()
        process(file_path, output_dir)
        end_time = time.time()
        avg_time += end_time - begin_time
        logging.warning("[time] process " + file + ", " + str(end_time - begin_time) + "(s)")

    logging.info("\nBatch spleeter done ! avg_time:"+ str(avg_time/f_n))
