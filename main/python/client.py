#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('../../thrift/gen-py')
import argparse
import time
import threading

from cv_common import VisionServices
from cv_types.ttypes import *

from thrift.transport import TSocket, TTransport
from thrift.protocol import TBinaryProtocol

import itertools
import multiprocessing as mp
result_queue = mp.Queue()


class ThriftProcessor(threading.local):
    def __init__(self, ip=None, port=None):
        self.host, self.port = ip, port
        #print('self.host, self.port is', self.host, self.port)
        self.transport = TSocket.TSocket(self.host, self.port)
        self.transport.setTimeout(1000000)
        self.transport = TTransport.TBufferedTransport(self.transport)
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.client = VisionServices.Client(self.protocol)
        self.transport.open()

    def __del__(self):
        self.transport.close()

    def process(self, req):
        #rsp = self.client.GetModelVersion(req)
        #rsp = self.client.Predict(req)
        rsp = self.client.SpeechDetect(req)
        return rsp


def get_args(model_status, ip, port, url, local_path):
    return model_status, ip, port, url, local_path


def query(status):
    model_status, ip, port, url, local_path = get_args(*status)
    global result_queue
    # 道玄：build up connection
    try:
        if args.run_local:
            client = ThriftProcessor(ip=ip, port=port)
        else:
            print('TODO: implement bilibili based thrift socket...')
    except Exception as e:
        print(e.what())

    #req = ModelVersionReq()
    '''
    req = VideoPredictReq()
    req.video_url = ''
    img = ImageInfo()
    img.image_url = 'http://www.xjdaily.com/upload/resources/image/2018/08/06/82665.jpg'
    req.frames.append(img)
    '''

    req = SpeechPredictReq()
    si = SpeechInfo()
    si.speech_url = url
    si.speech_path = local_path
    si.debug_path = '~/speech_debug_out_tmp/'  # just for debug

    req.info = si

    try:
        rsp = client.process(req)
        result_queue.put("%s\n" % rsp.model_version.model_version)
    except Exception as e:
        print(e.what())
    return


def write_to_file(result_path):
    global result_queue
    result = open(result_path, "w")
    while True:
        line = result_queue.get()
        if line != None:
            result.write(line)
        else:
            break
    result.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--test_num', default=20, type=int)
    parser.add_argument('--run_local', default=1, type=int)
    parser.add_argument('--run_par', default=0, type=int)
    parser.add_argument('--ip', required=True)
    parser.add_argument('--port', required=True)
    parser.add_argument('--url', required=False)
    parser.add_argument('--local_path', required=False)
    parser.add_argument('--debug', default=True, required=False)

    args = parser.parse_args()

    output_log = '../../service_log/client_log.txt'
    log_out = open(output_log, 'a')
    #print('branch:', args.run_par)
    time_cost = time.time()
    if args.run_par is 0:
        # 道玄：build up connection
        try:
            if args.run_local:
                client = ThriftProcessor(ip=args.ip, port=args.port)
            else:
                print('TODO: implement bilibili based thrift socket...')
        except Exception as e:
            print(e)
        for i in range(0, args.test_num):
            #req = ModelVersionReq()
            #req = VideoPredictReq()
            req = SpeechPredictReq()
            si = SpeechInfo()

            si.speech_url = args.url
            si.speech_path = args.local_path
            si.debug_path = '~/speech_debug_out_tmp/'  # just for debug

            input_file = open(args.local_path, 'rb')
            si.speech_data = input_file.read()
            input_file.close()

            req.info = si

            try:
                #
                print('------req-----:', req.info.speech_path, type(req.info.speech_data))
                rsp = client.process(req)
                print('++++++rsp+++++:', rsp)
                log_out.write('%s\n' % rsp.model_version.model_version)
            except Exception as e:
                print(e)
    else:
        # connection is built within every single thread
        data = zip(range(0, args.test_num), itertools.repeat(args.ip), itertools.repeat(args.port))
        write_p = mp.Process(target=write_to_file, args=(output_log,))
        write_p.start()
        p = mp.Pool(10)
        for one in data:
            p.apply_async(func=query, args=(one,))
        p.close()
        p.join()
        p.terminate()
        result_queue.put(None)
        write_p.join()
    time_cost = time.time() - time_cost
    print('[time cost]:', time_cost)
    log_out.close()

