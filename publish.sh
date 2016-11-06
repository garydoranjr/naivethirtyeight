#!/bin/bash

rsync -r -u --progress index.html figs gbd6@192.168.1.38:/var/www/naivethirtyeight.dyndns.org/
