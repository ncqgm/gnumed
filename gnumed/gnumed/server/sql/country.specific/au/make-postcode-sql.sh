#!/bin/sh

echo "re-generating postcodes.au.sql"
python postcode_import.py postcodes.au.csv | uniq > postcodes.au.sql 2> postcodes.au.log
