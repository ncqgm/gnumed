#!/bin/sh

export PYTHONPATH="${PYTHONPATH}:../../"

echo "re-bootstrapping maximum database"

./redo-public.sh

echo "adding on to standard (public) database to reach maximum database level"
echo "the following imports are likely to fail but are non-critical"

echo "-------------------"
echo "importing AMIS drug data"
./install_AMIS_data.sh
echo "--------------------"
echo "importing some BLOBs"
cd ~/Bilder/Vietnam/archive
python import-test-blobs.py
cd -
