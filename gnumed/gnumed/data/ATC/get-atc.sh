#!/bin/sh

wget -v -c http://freemedforms.googlecode.com/svn/trunk/global_resources/sql/atc_utf8.csv

grep --invert-match '^"Z.*","FREEDIAMS .*".*' atc_utf8.csv > atc_only-utf8.csv
