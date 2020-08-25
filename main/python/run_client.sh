#!/usr/bin/env bash
# 道玄：ip为服务器ip，本机测试时则为本机ip，端口port为服务启动时设置的端口

#echo 'run in order:'
#python client.py --test_num 20 --run_local 1 --run_par 0 \
#        --ip '169.254.136.35' --port '9416'
#
#echo ''
#echo 'run in parallel:'
#python client.py --test_num 20 --run_local 1 --run_par 1 \
#        --ip '169.254.136.35' --port '9416'

echo 'run in order:'
python3 client.py --test_num 1 --run_local 1 --run_par 0 \
        --ip '127.0.0.1' --port '9416'  --local_path '../../audios/千千阙歌.wav'

echo 'done'

#echo 'run in parallel:'
#python3 client.py --test_num 20 --run_local 1 --run_par 1 \
#        --ip '172.23.13.10' --port '9416'
