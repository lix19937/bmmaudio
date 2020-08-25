Audio Analyzer for vup


## About
This repo is for bmmaudioanalyzer project.  
A thrift based server is provoded by the project.  
First, spleeter to perform separation of audio files to 2 stems. Ex. Vocals (singing voice) / accompaniment separation (2 stems).  
Second, inaSpeechSegmenter splits audio signals into homogeneous zones of speech, music and noise.  


## Installation
install python=3.7.2  
install cudatoolkit=10.0.130  
install cudatoolkit-dev=10.0  
install cudnn=7.6.0  
install ffmpeg  

pip3 install keras==2.3.1 librosa==0.7.2 numba==0.48.0 matplotlib==3.2.0  
pip3 install thrift ffmpeg-python sidekit pyannote pandas  
pip3 install tensorflow-gpu==1.15.2  


## Quick start
After all dependencies are successfully installed, you should put some audio files in the audios folder.  
  
use follow:  
cd main/python  
sh ./run_server.sh  
sh ./run_client.sh  


