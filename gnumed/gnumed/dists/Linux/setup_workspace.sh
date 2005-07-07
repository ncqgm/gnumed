#!/bin/sh

# $Source: 
# $Id:

echo "____________"
echo "=> client <="
echo "============"


REV=0.1
rm -r ./GNUmed-$REV/client

mkdir -p ./GNUmed-$REV/client
mkdir -p ./GNUmed-$REV/client/usr/share/gnumed/
mkdir -p ./GNUmed-$REV/client/usr/share/doc/gnumed/client
mkdir -p ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/exporters/
mkdir -p ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/importers/
mkdir -p ./GNUmed-$REV/client/etc/gnumed/
mkdir -p ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/
mkdir -p ./GNUmed-$REV/client/usr/share/gnumed/pixmaps/
mkdir -p ./GNUmed-$REV/client/usr/bin/
mkdir -p ./GNUmed-$REV/client/usr/share/locale/de/LC_MESSAGES/
mkdir -p ./GNUmed-$REV/client/usr/share/locale/de_DE/LC_MESSAGES/
mkdir -p ./GNUmed-$REV/client/usr/share/locale/fr/LC_MESSAGES/
mkdir -p ./GNUmed-$REV/client/usr/share/locale/fr_FR/LC_MESSAGES/
mkdir -p ./GNUmed-$REV/client/usr/share/locale/es/LC_MESSAGES/
mkdir -p ./GNUmed-$REV/client/usr/share/locale/es_ES/LC_MESSAGES/

cp -R ../../client/bitmaps ./GNUmed-$REV/client/usr/share/gnumed/
cp -R ../../client/business ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/
cp -R ../../client/doc/medical_knowledge ./GNUmed-$REV/client/usr/share/doc/gnumed
cp -R ../../client/exporters/*.py ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/exporters/
cp -R ../../client/importers/*.py ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/importers/
cp -R ../../client/exporters/gmPatientExporter.conf ./GNUmed-$REV/client/etc/gnumed/
cp -R ../../client/etc/gnumed.conf.example ./GNUmed-$REV/client/etc/gnumed/gnumed.conf
cp -R ../../client/pycommon ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/
cp -R ../../client/wxpython ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/
cp -R ../../client/sitecustomize.py ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/
cp -R ../../client/__init__.py ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/
cp -R ./gnumed.xpm ./GNUmed-$REV/client/usr/share/gnumed/pixmaps/
cp -R ./gnumed ./GNUmed-$REV/client/usr/bin/
cp -R ../../../GnuPublicLicense.txt ./
cp -R ../../../check-prerequisites.py ./
cp -R ../../../check-prerequisites.sh ./

# build up2date *.po and *.mo language files
# ah maybe next time

cp ../../client/locale/de-gnumed.mo ./GNUmed-$REV/client/usr/share/locale/de/LC_MESSAGES/gnumed.mo
cp ../../client/locale/de-gnumed.mo ./GNUmed-$REV/client/usr/share/locale/de_DE/LC_MESSAGES/gnumed.mo
cp ../../client/locale/fr-gnumed.mo ./GNUmed-$REV/client/usr/share/locale/fr/LC_MESSAGES/gnumed.mo
cp ../../client/locale/fr-gnumed.mo ./GNUmed-$REV/client/usr/share/locale/fr_FR/LC_MESSAGES/gnumed.mo
cp ../../client/locale/es-gnumed.mo ./GNUmed-$REV/client/usr/share/locale/es/LC_MESSAGES/gnumed.mo
cp ../../client/locale/es-gnumed.mo ./GNUmed-$REV/client/usr/share/locale/es_ES/LC_MESSAGES/gnumed.mo

#----------------------------------
echo "____________"
echo "=> server <="
echo "============"

rm -r ./GNUmed-$REV/server
mkdir -p ./GNUmed-$REV/server
mkdir -p ./GNUmed-$REV/server/usr/lib/python/site-packages/Gnumed/
mkdir -p ./GNUmed-$REV/server/usr/share/gnumed/install/server/bootstrap

cp -R ../../client/pycommon ./GNUmed-$REV/server/usr/lib/python/site-packages/Gnumed/
cp -R ../../server/sql ./GNUmed-$REV/server/usr/share/gnumed/install/server
cp -R ../../server/bootstrap/ ./GNUmed-$REV/server/usr/share/gnumed/install/server/

echo "cleaning out debris"
find ./ -name '*.pyc' -exec rm -v '{}' ';'

#------------------------------------------
# $Log: setup_workspace.sh,v $
# Revision 1.1  2005-07-07 20:19:04  shilbert
# - script to create packaging environment
#
