#!/bin/sh

# $Source: 
# $Revision: 1.1 $
# GPL
# sebastian.hilbert@gmx.net

# todo: 
# log install path for uninstall file
# log installation

# change this to match GNUmed version
REV=0.1

echo "######################################################################################
#                                                                                    # 
# Welcome. You are about to install GNUmed. Please observe the output on the screen  #
# You will be prompted for target locations for GNUmed. The defaults provided give a #
# working setup on most systems and are considered safe. Your milage may vary.       #   
#                                                                                    #
#                                                      - GNUmed release team -       #
#                                                                                    #
######################################################################################"

mkdir -p /usr/lib/python/site-packages/Gnumed/
mkdir -p /usr/share/doc/gnumed/client
mkdir -p /usr/lib/python/site-packages/Gnumed/exporters/
mkdir -p /usr/lib/python/site-packages/Gnumed/importers/
mkdir -p /etc/gnumed/
mkdir -p /usr/lib/python/site-packages/Gnumed/
mkdir -p /usr/share/gnumed/pixmaps/
#mkdir -p ./GNUmed-$REV/client/usr/share/locale/de/LC_MESSAGES/
#mkdir -p ./GNUmed-$REV/client/usr/share/locale/de_DE/LC_MESSAGES/
#mkdir -p ./GNUmed-$REV/client/usr/share/locale/fr/LC_MESSAGES/
#mkdir -p ./GNUmed-$REV/client/usr/share/locale/fr_FR/LC_MESSAGES/
#mkdir -p ./GNUmed-$REV/client/usr/share/locale/es/LC_MESSAGES/
#mkdir -p ./GNUmed-$REV/client/usr/share/locale/es_ES/LC_MESSAGES/

#####################################

dfltgmdir=/usr/share/gnumed
echo "client bitmap target directory [$dfltgmdir]:" 
read newgmdir
if [ "$newgmdir" = "" ]; then
            gmdir=$dfltgmdir
else
            gmdir=$newgmdir
fi


cp -R ./GNUmed-$REV/client/usr/share/gnumed/bitmaps $gmdir
cp -R ./GNUmed-$REV/client/usr/share/gnumed/pixmaps/gnumed.xpm $gmdir/pixmaps/gnumed.xpm
#####################################
dfltpythondir=/usr/lib/python/site-packages/Gnumed
echo "python directory [$dfltpythondir]:" 
read newpythondir
if [ "$newpythondir" = "" ]; then
            pythondir=$dfltpythondir
else
            pythondir=$newpythondir
fi

cp -R ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/business $pythondir
cp -R ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/exporters/*.py $pythondir/exporters/
cp -R ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/importers/*.py $pythondir/importers/
cp -R ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/sitecustomize.py $pythondir
cp -R ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/pycommon $pythondir
cp -R ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/wxpython $pythondir
cp -R ./GNUmed-$REV/client/usr/lib/python/site-packages/Gnumed/__init__.py $pythondir
#######################################
dfltdocdir=/usr/share/doc/gnumed
echo "client documentation target directory [$dfltdocdir]:" 
read newdocdir
if [ "$newdocdir" = "" ]; then
            docdir=$dfltdocdir
else
            docdir=$newdocdir
fi
cp -R ./GNUmed-$REV/client/usr/share/doc/gnumed/medical_knowledge $docdir
cp -R ./GnuPublicLicense.txt $docdir
#######################################
dfltconfdir=/etc/gnumed
echo "client config files target directory [$dfltconfdir]:" 
read newconfdir
if [ "$newconfdir" = "" ]; then
            confdir=$dfltconfdir
else
            confdir=$newconfdir
fi

cp -R ./GNUmed-$REV/client/etc/gnumed/*.conf $confdir

#######################################
dfltlocaledir=/usr/share/locale
echo "client language files target directory [$dfltlocaledir]:" 
read newlocaledir
if [ "$newlocaledir" = "" ]; then
            localedir=$dfltlocaledir
else
            localedir=$newlocaledir
fi

cp -R ./GNUmed-$REV/client/usr/share/locale $localedir
#######################################

cp -R ./GNUmed-$REV/client/usr/bin/gnumed /usr/bin

# FIXME: put this some decent place
cp -R ./check-prerequisites.py /usr/bin
cp -R ./check-prerequisites.sh /usr/bin
