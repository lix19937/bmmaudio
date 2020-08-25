# coding=utf-8
# 参数1，原始音频文件目录
# 参数2，解析结果目录

import argparse
import json
import logging
import os
import warnings

import time
from pathlib import Path
from inaSpeechSegmenter import Segmenter

__input_file = ""
__out_dir = ""
__input_base_name = ""
__segmention = []
__result_json_file = ""
__result_dic = {}
__seg = None

def __prepare_pars(input, output, spleeter):
    global __input_file
    global __out_dir
    global __input_base_name
    global __result_json_file

    __input_file = input
    __out_dir = output
    __input_base_name = Path(__input_file).stem
    __result_json_file = __out_dir + "/" + __input_base_name  + ".json"
    logging.info("input :" + __input_file)
    logging.info("output dir :" + __out_dir)
    logging.info ("result json  " + __result_json_file)
    return True

def __prepare_segment(model_path):
    global __seg
    __seg = Segmenter(detect_gender=False, model_dir=model_path)

def __segment():
    global __seg
    global __segmention
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        __segmention = __seg(__input_file)
    return True

def __process_segmention():
    global __result_dic

    last_lable = ""
    last_start = -1
    last_end = -1
    segments = []
    __result_dic.clear()
    for segment in __segmention:
        label = segment[0]
        label = __map_label(label)
        start = round(float(segment[1]), 2)
        end = round(float(segment[2]), 2)
        if last_lable == "":
            last_lable = label
            last_start = start
            last_end = end
            continue
        if last_lable == label:
            last_end = end
            continue
        else:
            if last_lable == "speech":
                segments.append({"type":"speech", "startSec":last_start, "endSec":last_end})
            last_lable = label
            last_start = start
            last_end = end

    if last_lable == "speech":
        segments.append({"type":"speech", "startSec":last_start, "endSec":last_end})
    __result_dic["segments"] = segments

def __map_label(label):
    speech_labels = ["music", "speech"]
    if label in speech_labels:
        return "speech"
    return "noEnergy"


def clean():
    pass


def process(input, output, spleeter, log_time=False):
    __result_dic.clear()
    if not __prepare_pars(input, output, spleeter):
        logging.error("invalid args")
        return json.dumps(__result_dic)

    __result_dic["fileName"] = __input_base_name

    if not __segment():
        logging.error("segment failed")
        return json.dumps(__result_dic)

    __process_segmention()
    return json.dumps(__result_dic)

logging.basicConfig(level=logging.INFO)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.description='please enter two parameters input file and output dir'
    parser.add_argument("-i", "--input", help="input file", dest="input", type=str, default="/Users/lix/Desktop/fasic_cv_sdk/output/")
    parser.add_argument("-o", "--output", help="output dir", dest="output",  type=str, default="output/")
    parser.add_argument("-w", "--model_path", help="model dir", dest="model_path", type=str, default="/Users/lix/Desktop/fasic_cv_sdk/inaSpeechSegmenter/")
    args = parser.parse_args()
    if args.input == "" or args.output == "" or args.model_path == '':
        logging.error("input, output and spleeter dir can not be null")
        exit()
    
    prepare_begin = time.time()
    __prepare_segment(args.model_path)
    prepare_end = time.time()
    logging.warning("[time] prepare " + str(prepare_end - prepare_begin))

    input_dir = args.input
    files = os.listdir(input_dir)

    output_dir = args.output
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file in files:
        print('file name: %s' % file)
        if "vocals" not in file or "wav" not in file:
            continue
        process_begin = time.time()
        file_path = input_dir + "/" + file
        json_str = process(file_path, args.output, "'", log_time=True)
        result = open(__result_json_file, "w")
        result.write(json_str)
        result.close()
        process_end = time.time()
        logging.warning("[time] process " + file + ", time " + str(process_end - process_begin))
