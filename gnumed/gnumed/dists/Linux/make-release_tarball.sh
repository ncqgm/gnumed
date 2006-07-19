#!/bin/sh

#====================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/dists/Linux/make-release_tarball.sh,v $
# $Id: make-release_tarball.sh,v 1.1 2006-07-19 11:31:17 ncq Exp $
# license: GPL
#====================================================
REV=0.2

CLIENT_FILES_REMOVE=\
"../../client/business/gmForms.py "\
"../../client/business/README "\
"../../client/business/.py "\
"../../client/business/.py "\
"../../client/business/.py "\
"../../client/business/.py "\
"../../client/business/.py "\
"../../client/business/.py "\
"../../client/business/.py "\
" "\
" "\
" "\
" "\
" "\
" "\
" "\
" "\
" "\
" "\
" "\
" "\
" "\
" "\

echo "cleaning up"
rm -R ./GNUmed-$REV/*.*

# create client package
echo "____________"
echo "=> client <="
echo "============"

mkdir -p ./GNUmed-$REV/client/

cp -R ../../client/business ./GNUmed-$REV/client/
cp -R ../../client/etc/gnumed.conf.example ./GNUmed-$REV/client/

#mkdir -p ./GNUmed-$REV/client/usr/share/gnumed/
#mkdir -p ./GNUmed-$REV/client/usr/share/doc/gnumed/client
#mkdir -p ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/exporters/
#mkdir -p ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/importers/
#mkdir -p ./GNUmed-$REV/client/etc/gnumed/
#mkdir -p ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/
#mkdir -p ./GNUmed-$REV/client/usr/share/gnumed/pixmaps/
#mkdir -p ./GNUmed-$REV/client/usr/bin/
#mkdir -p ./GNUmed-$REV/client/usr/share/locale/de/LC_MESSAGES/
#mkdir -p ./GNUmed-$REV/client/usr/share/locale/de_DE/LC_MESSAGES/
#mkdir -p ./GNUmed-$REV/client/usr/share/locale/fr/LC_MESSAGES/
#mkdir -p ./GNUmed-$REV/client/usr/share/locale/fr_FR/LC_MESSAGES/
#mkdir -p ./GNUmed-$REV/client/usr/share/locale/es/LC_MESSAGES/
#mkdir -p ./GNUmed-$REV/client/usr/share/locale/es_ES/LC_MESSAGES/




cp -R ../../server/ ./GNUmed-$REV/
#cp -R ../../client/bitmaps ./GNUmed-$REV/client/bitmaps
#cp -R ../../client/business ./GNUmed-$REV/client/business
#cp -R ../../client/doc/medical_knowledge ./GNUmed-$REV/client/doc/medical_knowledge
#cp -R ../../client/exporters/*.py ./GNUmed-$REV/client/exporters/*.py
#cp -R ../../client/importers/*.py ./GNUmed-$REV/client/importers/*.py
#cp -R ../../client/exporters/gmPatientExporter.conf ./GNUmed-$REV/client/exporters/gmPatientExporter.conf
#cp -R ../../client/gm-0_1.conf ./GNUmed-$REV/client/gm-0_1.conf
#cp -R ../../client/pycommon ./GNUmed-$REV/client/pycommon
#cp -R ../../client/wxpython ./GNUmed-$REV/client/wxpython
#cp -R ../../client/sitecustomize.py ./GNUmed-$REV/client/sitecustomize.py
#cp -R ../../client/__init__.py ./GNUmed-$REV/client/__init__.py
#cp -R ./gnumed.xpm ./GNUmed-$REV/client/gnumed.xpm
cp -R ./gnumed ./GNUmed-$REV/client/gnumed

# copy user manual from wiki
echo "downloading Manual zip file from the web"
rm -vf Main.TWikiGuest_Gnumed.zip
wget -v http://salaam.homeunix.com/gm-manual/Main.TWikiGuest_Gnumed.zip
unzip Main.TWikiGuest_Gnumed.zip -d ./GNUmed-$REV/user-manual
cd ./GNUmed-$REV/client/user-manual/
ln -s Release-01.html index.html
cd -

# build up2date *.po and *.mo language files
cd ./GNUmed-$REV/client/locale/
./create-gnumed_mo.sh de
./create-gnumed_mo.sh es
./create-gnumed_mo.sh fr
cd -

#cp ../../client/locale/de-gnumed.mo ./GNUmed-$REV/locale/de/LC_MESSAGES/gnumed.mo
#cp ../../client/locale/de-gnumed.mo ./GNUmed-$REV/locale/de_DE/LC_MESSAGES/gnumed.mo
#cp ../../client/locale/fr-gnumed.mo ./GNUmed-$REV/locale/fr/LC_MESSAGES/gnumed.mo
#cp ../../client/locale/fr-gnumed.mo ./GNUmed-$REV/locale/fr_FR/LC_MESSAGES/gnumed.mo
#cp ../../client/locale/es-gnumed.mo ./GNUmed-$REV/locale/es/LC_MESSAGES/gnumed.mo
#cp ../../client/locale/es-gnumed.mo ./GNUmed-$REV/locale/es_ES/LC_MESSAGES/gnumed.mo

#----------------------------------
echo "____________"
echo "=> server <="
echo "============"

#mkdir -p ./GNUmed-$REV/server
#mkdir -p ./GNUmed-$REV/server/usr/lib/python/site-packages/Gnumed/
#mkdir -p ./GNUmed-$REV/server/usr/share/gnumed/install/server/bootstrap

#cp -R ../../client/pycommon ./GNUmed-$REV/server/usr/lib/python/site-packages/Gnumed/
cp -R ../../server/ ./GNUmed-$REV/server/
#cp -R ../../server/bootstrap/ ./GNUmed-$REV/server/usr/share/gnumed/install/server/

#----------------------------------
cp -R ../../../GnuPublicLicense.txt ./GNUmed-$REV/
cp -R ../../../check-prerequisites.py ./GNUmed-$REV/
cp -R ../../../check-prerequisites.sh ./GNUmed-$REV/
cp -R ../../../CHANGELOG ./GNUmed-$REV/
#cp -R ./install.sh ./GNUmed-$REV/
#ln -s ../CHANGELOG ../check-prerequisites.py ../check-prerequisites.sh ../install.sh ../GnuPublicLicense.txt ./GNUmed-$REV/

#----------------------------------
echo "cleaning out debris"
find ./ -name '*.pyc' -exec rm -v '{}' ';'
find ./ -name '*.log' -exec rm -v '{}' ';'
find ./GNUmed-$REV/ -name 'CVS' -type d -exec rm -v -r '{}' ';'
find ./GNUmed-$REV/ -name 'wxg' -type d -exec rm -v -r '{}' ';'

#------------------------------------------
# $Log: make-release_tarball.sh,v $
# Revision 1.1  2006-07-19 11:31:17  ncq
# - renamed to better reflect its use
#
# Revision 1.1  2006/06/21 21:58:13  shilbert
# - cosmetic changes
#
# Revision 1.10  2006/02/12 18:07:42  shilbert
# - nearing v0.2
#
# Revision 1.9  2005/08/24 09:33:53  ncq
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
