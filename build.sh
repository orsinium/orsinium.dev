#!/bin/bash
python3 -m pip install -r requirements.txt
python3 meta.py
python3 missed.py
python3 generate.py
