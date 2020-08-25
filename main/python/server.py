#!/usr/bin/env python
import sys
sys.path.append('../../thrift/gen-py')
sys.path.append('../../')

import argparse
import time
import random

from cv_common import VisionServices
from cv_types.ttypes import *

from thrift.transport import TSocket, TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

import os
import shutil
from logger import get_logger
from audio_detect import AudioDetect

##
##
## lsof -i :9416  kill -9 pid
##


def get_args():
    parser = argparse.ArgumentParser(description='Face Recognition Server')
    parser.add_argument('--port', type=int, default=9416, help='Server Port, default = 9416')
    parser.add_argument('--worker', type=int, default=1, help='Process worker number')
    args = parser.parse_args()
    return args.port, args.worker


class VisionServicesHandler:
    def __init__(self, conf_path_1, conf_path_2, info_logger=None, error_logger=None):
        self.info_logger = info_logger
        self.error_logger = error_logger
        self.conf_path_1 = conf_path_1
        self.conf_path_2 = conf_path_2

        try:
            self.engine = AudioDetect(self.conf_path_1, self.conf_path_2) ######only one
        except:
            raise RuntimeError('engine init failed')

        error_code = self.load_model()
        if 0 != error_code:
            raise RuntimeError('load model failed')
        print('server conf init done')

    def load_model(self):
        #
        # read  netcfg , weights , labels
        #
        return 0

    def parser_input(self, req):
        #
        # make input to net input tensor
        #
        return 0

    def parser_output(self, rsp):
        #
        # make rsp to user data
        #
        return 0

    def Predict(self, req):
        self.parser_input(req)

        print('Predict overload here')
        rsp = VideoTagPredictRsp()
        rsp.model_version = ModelVersion()

        self.parser_output(rsp)

        #
        rsp.model_version.model_version = 'bilibili 1.0.0 videotag test, stub'
        tpr = TagPredictResult()

        tp = TagPredict()
        tp.tag_id = 1
        tp.prob = 0.96

        tpr.predicts = []
        tpr.predicts.append(tp)
        tpr.embeding = []
        tpr.embeding.append(1.)
        rsp.predict_results = []
        rsp.predict_results.append(tpr)

        #tpr.predicts.insert(tp)
        #tpr.embeding.insert(1.)
        #rsp.predict_results.insert(tpr)

        wait_time = random.random()
        time.sleep(wait_time)
        return rsp

    def SpeechDetect(self, req):
        self.parser_input(req)
        rsp = SpeechDetRsp()
        rsp.json_str = ''
        print('para:', req.info.speech_path, req.info.debug_path, type(req.info.speech_data))
        if not os.path.exists(req.info.debug_path):
            os.makedirs(req.info.debug_path)
        #try:
        # speech_path is audio file
        # debug_path is a dir which save fragments of audio
        #rsp.json_str = self.engine.process(req.info.speech_path, req.info.debug_path)#############

        rsp.json_str = self.engine.process_from_buffer(req.info.speech_data, req.info.speech_path)

        #except:
            #print('process error')
        rsp.model_version = ModelVersion()
        rsp.model_version.model_version = 'bilibili 1.0.0 speech test'

        wait_time = random.random()
        time.sleep(wait_time)
        return rsp

    def __del__(self):
        return
    '''
    def GetModelVersion(self, req): # overload
        model_id = req.status
        rsp = ModelVersionRsp()
        rsp.model_version = ModelVersion()
        rsp.model_version.model_version = '0.0.' + model_id + ' for test!'
        print('rsp====', model_id, ' ,', rsp.model_version.model_version)

        # this is for multi threads testing
        wait_time = random.random()  # [0,1)
        time.sleep(wait_time)
        return rsp
    '''

if __name__ == '__main__':
    if os.path.exists('../../service_log'):
        shutil.rmtree('../../service_log')
    os.makedirs('../../service_log/info_log')
    os.makedirs('../../service_log/error_log')
    info_logger = get_logger(
        name=__name__ + '_info', filename='../../service_log/info_log/info.log', level='info')
    error_logger = get_logger(
        name=__name__ + '_error',
        filename='../../service_log/error_log/error.log',
        level='error')

    #
    conf_path_1 = '/Users/lix/Desktop/fasic_cv_sdk/pretrained_models/2stems'
    conf_path_2 = '/Users/lix/Desktop/fasic_cv_sdk/inaSpeechSegmenter'

    handler = VisionServicesHandler(conf_path_1, conf_path_2, info_logger=info_logger, error_logger=error_logger)
    processor = VisionServices.Processor(handler)

    port, worker = get_args()
    transport = TSocket.TServerSocket(port=port)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory(strictRead=True, strictWrite=False)
    server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)
    print('server starting...')
    server.serve()

