#!/usr/bin/env bash

thrift -gen py base.thrift
thrift -gen py cv_types.thrift
thrift -gen py cv_common.thrift

#
#  gen-py  存放的中间文件
#
#
#编译thrift文件，生成C++代码：
#
#./thrift --gen cpp tutorial.thrift　　 #结果代码存放在gen-cpp目录下
#
#
#如果是要生成java代码：
#
#./thrift --gen java tutorial.thrift　　#结果代码存放在gen-java目录下
#
#
#