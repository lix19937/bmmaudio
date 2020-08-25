
import argparse
import json
import logging

import warnings
import time
from pathlib import Path
from inaSpeechSegmenter import Segmenter
from spleeter.separator import Separator

logging.basicConfig(level=logging.INFO)

import buffer_utils
import os
# import ssl
# ssl._create_default_https_context = ssl._create_unverified_context


class AudioDetect:

    def __init__(self, model_path_1, model_path_2):
        self.spleeter = Separator('spleeter:2stems', model_path_1)
        # 基于频域进行音轨分离,分离人声的话一般只需要2轨,accompaniment.wav  提取的背景/伴奏； vocals.wav是提取的人声
        self.spleeter._get_predictor()

        self.ina_speech_segmenter = Segmenter(detect_gender=False, model_dir=model_path_2) ######
        logging.info("init done")

    def file_base_name(self, file_path):
        return Path(file_path).resolve().stem

    def spleeter_volcals_file_name(self, input_file, output_dir):
        input_base_name = self.file_base_name(input_file)
        return output_dir + "/" + input_base_name + "/vocals.wav"  # get

    def do_spleeter_from_buffer(self, input_buffer):
        waveform = buffer_utils.buffer_to_wave_for_spleeter(input_buffer, 44100)
        sources = self.spleeter.separate(waveform)
        return sources['vocals']

    def do_spleeter(self, input_file, out_dir):  # 分轨文件目录 out_dir
        self.spleeter.separate_to_file(input_file, out_dir, filename_format='{filename}/{instrument}.{codec}')
        return True

    def do_segment_from_buffer(self, input_buffer):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            mspec, loge, difflen = buffer_utils.feat_from_spleeter_vocals_for_segment_two_transcode(input_buffer)
            segmention = self.ina_speech_segmenter.segment_feats(mspec, loge, difflen, 0)
        return (True, segmention)

    def do_segment(self, input, output_dir):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            segmention = self.ina_speech_segmenter(self.spleeter_volcals_file_name(input, output_dir))

        return (True, segmention)

    def process_segmention(self, result_dic, segmention):
        last_lable = ""
        last_start = -1
        last_end = -1
        segments = []
        for segment in segmention:
            label = segment[0]
            label = self.map_label(label)
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
                    segments.append({"type": "speech", "startSec": last_start, "endSec": last_end})
                last_lable = label
                last_start = start
                last_end = end

        if last_lable == "speech":
            segments.append({"type": "speech", "startSec": last_start, "endSec": last_end})
        result_dic["segments"] = segments

    def map_label(self, label):
        speech_labels = ["music", "speech"]
        if label in speech_labels:
            return "speech"
        return "noEnergy"

    def process_from_buffer(self, input_buffer, input_file):
        result_dic = {}
        result_dic.clear()
        input_base_name = os.path.basename(input_file)
        result_dic["fileName"] = input_base_name

        vocals_data = self.do_spleeter_from_buffer(input_buffer)
        if vocals_data is None:
            logging.error("separate failed")
            return json.dumps(result_dic, ensure_ascii=False)

        result, segmention = self.do_segment_from_buffer(vocals_data) # make sure vocals_data is 16kHz
        if not result:
            logging.error("segment failed")
            return json.dumps(result_dic, ensure_ascii=False)

        self.process_segmention(result_dic, segmention)
        return json.dumps(result_dic, ensure_ascii=False)

    def process(self, input, output):
        result_dic = {}
        result_dic.clear()
        input_base_name = os.path.basename(input)
        result_dic["fileName"] = input_base_name

        if not self.do_spleeter(input, output):            ### step 1
            logging.error("separate failed")
            return json.dumps(result_dic, ensure_ascii=False)

        result, segmention = self.do_segment(input, output) ### step 2
        if not result:
            logging.error("segment failed")
            return json.dumps(result_dic, ensure_ascii=False)

        self.process_segmention(result_dic, segmention)
        return json.dumps(result_dic, ensure_ascii=False)

def main():
    parser = argparse.ArgumentParser()
    parser.description = 'please enter two parameters input file and output dir'
    parser.add_argument("-i", "--input",  help="input file", dest="input",   type=str, default="output/")
    parser.add_argument("-o", "--output", help="output dir", dest="output",  type=str, default="result/")
    args = parser.parse_args()
    if args.input == "" or args.output == "":
        logging.error("input, output dir can not be null")
        exit()
    model_path_1 = '/Users/lix/Desktop/fasic_cv_sdk/pretrained_models/2stems'
    model_path_2 = '/Users/lix/Desktop/fasic_cv_sdk/inaSpeechSegmenter'
    ##############
    audio_detect = AudioDetect(model_path_1, model_path_2)

    input_dir = args.input
    output_dir = args.output
    files = os.listdir(args.input)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file in files:
        print('file_name: %s' % file)
        if not "wav" in file:
            continue
        file_path = input_dir + "/" + file
        begin_time = time.time()
        # use file from disk
        #str_json = audio_detect.process(file_path, output_dir)

        # use memory buffer
        if 1:
            input_file = open(file_path, 'rb')
            input_buffer = input_file.read()
            input_file.close()
            str_json = audio_detect.process_from_buffer(input_buffer, file_path)

        #########################
        input_base_name = audio_detect.file_base_name(file_path)
        json_file = os.path.join(
            output_dir, input_base_name+"_result.json"
        )
        with open(json_file, 'w') as f:
            f.write(str_json)
        end_time = time.time()
        logging.warning("[time] process " + file + ", " + str(end_time - begin_time) + "(s)")
        break

if __name__ == "__main__":
    main()


