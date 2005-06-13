#!/bin/sh

# $Source: 
# $Revision: 

echo "setting up workspace"
cp -R ../../client/bitmaps ./GNUmed/
cp -R ../../client/business ./GNUmed/
cp -R ../../client/doc ./GNUmed/
cp -R ../../client/locale ./GNUmed/
cp -R ../../client/pycommon ./GNUmed/
cp -R ../../client/wxpython ./GNUmed/

echo "cleaning out debris"
find ./ -name '*.pyc' -exec rm -v '{}' ';'
