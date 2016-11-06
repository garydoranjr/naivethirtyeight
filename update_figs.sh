#!/bin/bash

python simulate_president.py -o auto
python simulate_senate.py -o auto
python update_html.py
