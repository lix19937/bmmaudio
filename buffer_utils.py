# coding: utf8

import argparse
import ffmpeg
import numpy as np
import logging
import struct
from sidekit.frontend.features import mfcc
import warnings

def __to_ffmpeg_time(n):
    m, s = divmod(n, 60)
    h, m = divmod(m, 60)
    return '%d:%02d:%09.6f' % (h, m, s)

def buffer_to_wave_for_spleeter(input_buffer, sample_rate=44100, dtype=np.float32):
    # convert buffer from audio file to wave
    # offset=0, duration=600,
    output_kwargs = {'format': 'f32le', 'ar': sample_rate}
    # if duration is not None:
    #     output_kwargs['t'] = __to_ffmpeg_time(duration)
    # if offset is not None:
    #     output_kwargs['ss'] = __to_ffmpeg_time(offset)

    n_channels = 2
    process = (
        ffmpeg
        .input('pipe:')
        .output('pipe:', **output_kwargs)
        .run_async(pipe_stdin=True, pipe_stderr=True, pipe_stdout=True, quiet=False))
    try:
        output_buffer, _ = process.communicate(input=input_buffer)
        waveform = np.frombuffer(output_buffer, dtype='<f4').reshape(-1, n_channels)
        if not waveform.dtype == np.dtype(dtype):
            waveform = waveform.astype(dtype)
        return waveform
    except IOError:
        logging.error(f'FFMPEG error: {process.stderr.read()}')
        return None

def load(path, offset=0, duration=600, sample_rate=44100, dtype=np.float32):
    n_channels = 2
    output_kwargs = {'format': 'f32le', 'ar': sample_rate}
    if duration is not None:
        output_kwargs['t'] = __to_ffmpeg_time(duration)
    if offset is not None:
        output_kwargs['ss'] = __to_ffmpeg_time(offset)

    process = (
        ffmpeg
        .input(path)
        .output('pipe:', **output_kwargs)
        .run_async(pipe_stdout=True, pipe_stderr=True))

    buffer, _ = process.communicate()
    waveform = np.frombuffer(buffer, dtype='<f4').reshape(-1, n_channels)
    if not waveform.dtype == np.dtype(dtype):
        waveform = waveform.astype(dtype)
    return waveform

def feat_from_raw(raw): # see features.py
    sampwidth = 2
    nchannels = 1
    nframes = len(raw) / sampwidth
    out = struct.unpack_from("%dh" % nframes * nchannels, raw)
    sig = np.reshape(np.array(out), (-1, nchannels)).squeeze()
    sig = sig.astype(np.float32)
    shp = sig.shape
    # wav should contain a single channel
    assert len(shp) == 1 or (len(shp) == 2 and shp[1] == 1)
    sig *= (2**(15-sampwidth))

    with warnings.catch_warnings() as w:
        # ignore warnings resulting from empty signals parts
        warnings.filterwarnings(
            'ignore', message='divide by zero encountered in log', category=RuntimeWarning, module='sidekit')
        _, loge, _, mspec = mfcc(sig.astype(np.float32), get_mspec=True)

    # Management of short duration segments
    difflen = 0
    if len(loge) < 68:
        difflen = 68 - len(loge)
        warnings.warning(
            "media %s duration is short. Robust results require length of at least 720 milliseconds" % wavname)
        mspec = np.concatenate(
            (mspec, np.ones((difflen, 24)) * np.min(mspec)))
        #loge = np.concatenate((loge, np.ones(difflen) * np.min(mspec)))

    return mspec, loge, difflen

def feat_from_buffer_for_segment(input_buffer):
    # get feature from buffer
    framerate = 16000
    nchannels = 1
    output_kwargs = {'ac': nchannels, 'ar': framerate, 'f': 's16le'}
    process = (
        ffmpeg
        .input('pipe:')
        .output('pipe:', **output_kwargs)
        .run_async(pipe_stdin=True, pipe_stderr=True, pipe_stdout=True, quiet=False))
    try:
        raw, _ = process.communicate(input=input_buffer)
        mspec, loge, difflen = feat_from_raw(raw)
        return mspec, loge, difflen
    except IOError:
        logging.error(f'FFMPEG error: {process.stderr.read()}')
        return None, None, None

def feat_from_spleeter_vocals_for_segment(vocals_data, sample_rate=44100):
    # get feature from buffer
    # 44100Hz、2 channels、f32le ——>16000Hz、1 channel、s16le
    framerate = 16000
    nchannels = 1
    input_kwargs = {'ar': sample_rate, 'ac': vocals_data.shape[1]}
    output_kwargs = {'ac': nchannels, 'ar': framerate, 'f': 's16le'}
    process = (
        ffmpeg
        .input('pipe:', format='f32le', **input_kwargs)
        .output('pipe:', **output_kwargs)
        .run_async(pipe_stdin=True, pipe_stderr=True, pipe_stdout=True, quiet=False))
    try:
        raw, _ = process.communicate(input=vocals_data.astype('<f4').tobytes()) ###
        return feat_from_raw(raw)
    except IOError:
        logging.error(f'FFMPEG error: {process.stderr.read()}')
        return None, None, None


def feat_from_spleeter_vocals_for_segment_two_transcode(vocals_data, sample_rate=44100):
    # get feature from buffer
    # 44100Hz、2 channels、f32le ——> 44100Hz、2 channels、s16le ——>16000Hz、1 channel、s16le
    framerate = 16000
    nchannels = 1
    input_kwargs = {'ar': sample_rate, 'ac': vocals_data.shape[1]}
    output_kwargs = {'ac': 2, 'ar': 44100, 'f': 's16le'}
    process = (
        ffmpeg
        .input('pipe:', format='f32le', **input_kwargs)
        .output('pipe:', **output_kwargs)
        .run_async(pipe_stdin=True, pipe_stderr=True, pipe_stdout=True, quiet=False))
    try:
        raw, _ = process.communicate(input=vocals_data.astype('<f4').tobytes())
        input_kwargs = {'ar': 44100, 'ac': 2}
        output_kwargs = {'ac': nchannels, 'ar': framerate, 'f': 's16le'}
        process = (
            ffmpeg
            .input('pipe:', format='s16le', **input_kwargs)
            .output('pipe:', **output_kwargs)
            .run_async(pipe_stdin=True, pipe_stderr=True, pipe_stdout=True, quiet=False))
        raw_two_transcode, _ = process.communicate(input=raw)
        return feat_from_raw(raw_two_transcode)
    except IOError:
        logging.error(f'FFMPEG error: {process.stderr.read()}')
        return None, None, None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.description = 'please enter two parameters input file and output dir'
    parser.add_argument("-i", "--input", help="input file",
                        dest="input", type=str, default="output/speech.wav")

    args = parser.parse_args()
    if args.input == "":
        logging.error("input can not be null")
    input_file = args.input

    input_file = open(args.input, "rb")
    input_buffer = input_file.read()
    logging.info("input buffer " + str(len(input_buffer)))
    input_file.close()

    # feat_from_buffer_for_segment(input_buffer)
    wav = buffer_to_wave_for_spleeter(input_buffer)
    wav2 = load(args.input)

    if wav.all() == wav2.all():
        print('ok')
    print('done')

