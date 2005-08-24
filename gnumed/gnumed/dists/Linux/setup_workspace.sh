#!/bin/sh

#====================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/dists/Linux/Attic/setup_workspace.sh,v $
# $Id: setup_workspace.sh,v 1.9 2005-08-24 09:33:53 ncq Exp $
# license: GPL
#====================================================
REV=0.1

# clean up
rm -r ./GNUmed-$REV/

# create client package
echo "____________"
echo "=> client <="
echo "============"

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
cp -R ../../client/gm-0_1.conf ./GNUmed-$REV/client/etc/gnumed/gnumed.conf
cp -R ../../client/pycommon ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/
cp -R ../../client/wxpython ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/
cp -R ../../client/sitecustomize.py ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/
cp -R ../../client/__init__.py ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/
cp -R ./gnumed.xpm ./GNUmed-$REV/client/usr/share/gnumed/pixmaps/
cp -R ./gnumed ./GNUmed-$REV/client/usr/bin/

# copy user manual from wiki
echo "downloading Manual zip file from the web"
rm -vf Main.TWikiGuest_Gnumed.zip
wget -v http://salaam.homeunix.com/gm-manual/Main.TWikiGuest_Gnumed.zip
unzip Main.TWikiGuest_Gnumed.zip -d ./GNUmed-$REV/client/usr/share/doc/gnumed/client/user-manual
cd ./GNUmed-$REV/client/usr/share/doc/gnumed/client/user-manual/
ln -s Release-01.html index.html
cd -

# build up2date *.po and *.mo language files
cd ../../client/locale/
./create-gnumed_mo.sh de
./create-gnumed_mo.sh es
./create-gnumed_mo.sh fr
cd -

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

mkdir -p ./GNUmed-$REV/server
mkdir -p ./GNUmed-$REV/server/usr/lib/python/site-packages/Gnumed/
mkdir -p ./GNUmed-$REV/server/usr/share/gnumed/install/server/bootstrap

cp -R ../../client/pycommon ./GNUmed-$REV/server/usr/lib/python/site-packages/Gnumed/
cp -R ../../server/sql ./GNUmed-$REV/server/usr/share/gnumed/install/server
cp -R ../../server/bootstrap/ ./GNUmed-$REV/server/usr/share/gnumed/install/server/

#----------------------------------
cp -R ../../../GnuPublicLicense.txt ./GNUmed-$REV/
cp -R ../../../check-prerequisites.py ./GNUmed-$REV/
cp -R ../../../check-prerequisites.sh ./GNUmed-$REV/
cp -R ../../../CHANGELOG ./GNUmed-$REV/

#ln -s ../CHANGELOG ../check-prerequisites.py ../check-prerequisites.sh ../install.sh ../GnuPublicLicense.txt ./GNUmed-$REV/

#----------------------------------
echo "cleaning out debris"
find ./ -name '*.pyc' -exec rm -v '{}' ';'
find ./GNUmed-$REV/ -name 'CVS' -type d -exec rm -v -r '{}' ';'

#------------------------------------------
# $Log: setup_workspace.sh,v $
# Revision 1.9  2005-08-24 09:33:53  ncq
# - remove CVS/ debris as requested by Debian packager
#
# Revision 1.8  2005/08/22 13:51:11  ncq
# - include CHANGELOG
#
# Revision 1.7  2005/07/19 20:43:21  ncq
# - make index.html link to Release-0.1.html
#
# Revision 1.6  2005/07/19 17:16:06  shilbert
# - gmManual now actually displays some content again
#
# Revision 1.5  2005/07/19 15:31:14  ncq
# - retrieve manual zip file from the web with wget
#
# Revision 1.4  2005/07/16 10:56:38  shilbert
# - copy user manual from wiki to workplace
#
# Revision 1.3  2005/07/10 18:46:39  ncq
# - build mo-files, too
#
# Revision 1.2  2005/07/10 17:42:32  ncq
# - move README style files directly below GNUmed-0.1 directory
#
# Revision 1.1  2005/07/07 20:19:04  shilbert
# - script to create packaging environment
#
