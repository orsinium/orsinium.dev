#!/bin/bash
echo "# update meta"
python3 meta.py
echo "# show missed"
python3 missed.py
echo "# generate HTML pages"
python3 generate.py
