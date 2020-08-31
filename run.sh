#!/bin/bash
python3 ftp-harvest/run.py -l && { python3 ftp-harvest/run.py -b 30 & python3 ./main.py; }

