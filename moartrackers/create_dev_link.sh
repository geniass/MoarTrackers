#!/bin/bash
cd /home/ari/development/deluge-plugins/MoarTrackers/moartrackers
mkdir temp
export PYTHONPATH=./temp
/usr/bin/python setup.py build develop --install-dir ./temp
cp ./temp/MoarTrackers.egg-link /home/ari/.config/deluge/plugins
rm -fr ./temp
