#!/usr/bin/env bash
# SDR 数据桥接一键启动
cd "$(dirname "$0")/tcp"
export PYTHONPATH="..:/usr/lib/python3/dist-packages:$PYTHONPATH"
exec python3 tcp_launch.py
