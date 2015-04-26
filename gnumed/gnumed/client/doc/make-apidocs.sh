#!/bin/bash

# license: GPL v2 or later
# author: Karsten.Hilbert@gmx.net

cd ~/gm-git/gnumed/gnumed/
ln -sT client Gnumed
cd -
BASE=~/gm-git/gnumed/gnumed/Gnumed
#MODULES=" $BASE/pycommon/ $BASE/business/ $BASE/connectors/ $BASE/exporters/ $BASE/importers/ $BASE/wxpython/"
LOG=~/gm-apidocs/epydoc-errors.txt

export DISPLAY=":0.0"
export PYTHONPATH="${PYTHONPATH}:~/gm-git/gnumed/gnumed/"
mkdir ~/gm-apidocs
nice -n 19 epydoc -v --debug --show-imports -n "GNUmed Never Sleeps" -u http://www.gnumed.org --no-private -o ~/gm-apidocs $BASE/ &> $LOG
cat $LOG
