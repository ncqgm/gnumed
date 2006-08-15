#!/bin/sh

#====================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/dists/Linux/make-release_tarball.sh,v $
# $Id: make-release_tarball.sh,v 1.15.2.1 2006-08-15 21:15:34 ncq Exp $
# license: GPL
#====================================================
REV="0.2"
CLIENTARCH="GNUmed-client.$REV.tgz"
SRVARCH="GNUmed-server.$REV.tgz"

FILES_REMOVE=\
"./GNUmed-$REV/client/business/README "\
"./GNUmed-$REV/client/business/gmForms.py "\
"./GNUmed-$REV/client/business/gmOrganization.py "\
"./GNUmed-$REV/client/business/gmXmlDocDesc.py "\
"./GNUmed-$REV/client/pycommon/gmDrugObject.py "\
"./GNUmed-$REV/client/pycommon/gmDrugView.py "\
"./GNUmed-$REV/client/pycommon/gmSchemaRevisionCheck.py "\
"./GNUmed-$REV/client/pycommon/gmSerialTools.py "\
"./GNUmed-$REV/client/pycommon/gmTrace.py "\
"./GNUmed-$REV/client/pycommon/gmdbf.py "\
"./GNUmed-$REV/client/wxGladeWidgets/README.py "\
"./GNUmed-$REV/client/wxGladeWidgets/wxgAU_AdminLoginV01.py "\
"./GNUmed-$REV/client/wxGladeWidgets/wxgAU_DBUserSetupV01.py "\
"./GNUmed-$REV/client/wxGladeWidgets/wxgAU_StaffMgrPanel.py "\
"./GNUmed-$REV/client/wxGladeWidgets/wxgAU_StaffV01.py "\
"./GNUmed-$REV/client/wxGladeWidgets/wxgRequest.py "\
"./GNUmed-$REV/client/wxpython/gmAU_VaccV01.py "\
"./GNUmed-$REV/client/wxpython/gmAllergyWidgets.py "\
"./GNUmed-$REV/client/wxpython/gmBMIWidgets.py "\
"./GNUmed-$REV/client/wxpython/gmCharacterValidator.py "\
"./GNUmed-$REV/client/wxpython/gmCryptoText.py "\
"./GNUmed-$REV/client/wxpython/gmFormPrinter.py "\
"./GNUmed-$REV/client/wxpython/gmGP_ActiveProblems.py "\
"./GNUmed-$REV/client/wxpython/gmGP_FamilyHistorySummary.py "\
"./GNUmed-$REV/client/wxpython/gmGP_HabitsRiskFactors.py "\
"./GNUmed-$REV/client/wxpython/gmGP_Inbox.py "\
"./GNUmed-$REV/client/wxpython/gmGP_PatientPicture.py "\
"./GNUmed-$REV/client/wxpython/gmGP_SocialHistory.py "\
"./GNUmed-$REV/client/wxpython/gmLabWidgets.py "\
"./GNUmed-$REV/client/wxpython/gmListCtrlMapper.py "\
"./GNUmed-$REV/client/wxpython/gmMultiColumnList.py.py "\
"./GNUmed-$REV/client/wxpython/gmMultiSash.py "\
"./GNUmed-$REV/client/wxpython/gmPatientHolder.py "\
"./GNUmed-$REV/client/wxpython/gmPlugin_Patient.py "\
"./GNUmed-$REV/client/wxpython/gmPregWidgets.py "\
"./GNUmed-$REV/client/wxpython/gmSelectPerson.py "\
"./GNUmed-$REV/client/wxpython/gmShadow.py "\
"./GNUmed-$REV/client/wxpython/gmSQLListControl.py "\
"./GNUmed-$REV/client/wxpython/gmSQLSimpleSearch.py "\
"./GNUmed-$REV/client/wxpython/gui/gmAllergiesPlugin.py "\
"./GNUmed-$REV/client/wxpython/gui/gmAU_VaccV01Plugin.py "\
"./GNUmed-$REV/client/wxpython/gui/gmClinicalWindowManager.py "\
"./GNUmed-$REV/client/wxpython/gui/gmContacts.py "\
"./GNUmed-$REV/client/wxpython/gui/gmDemographicsEditor.py "\
"./GNUmed-$REV/client/wxpython/gui/gmDrugDisplay.py "\
"./GNUmed-$REV/client/wxpython/gui/gmEMRTextDumpPlugin.py "\
"./GNUmed-$REV/client/wxpython/gui/gmGuidelines.py "\
"./GNUmed-$REV/client/wxpython/gui/gmLabJournal.py "\
"./GNUmed-$REV/client/wxpython/gui/gmMultiSashedProgressNoteInputPlugin.py "\
"./GNUmed-$REV/client/wxpython/gui/gmOffice.py "\
"./GNUmed-$REV/client/wxpython/gui/gmPython.py "\
"./GNUmed-$REV/client/wxpython/gui/gmRequest.py "\
"./GNUmed-$REV/client/wxpython/gui/gmShowLab.py "\
"./GNUmed-$REV/client/wxpython/gui/gmSnellen.py "\
"./GNUmed-$REV/client/wxpython/gui/gmSQL.py "\
"./GNUmed-$REV/client/wxpython/gui/gmStikoBrowser.py "\
"./GNUmed-$REV/client/wxpython/gui/gmVaccinationsPlugin.py "\
"./GNUmed-$REV/client/wxpython/gui/gmXdtViewer.py "\
"./GNUmed-$REV/server/bootstrap/amis-config.set "\
"./GNUmed-$REV/server/bootstrap/bootstrap-amis.conf "\
"./GNUmed-$REV/server/bootstrap/bootstrap-archive.conf "\
"./GNUmed-$REV/server/bootstrap/install_AMIS_data.sh "\
"./GNUmed-$REV/server/bootstrap/redo-max.sh "\
"./GNUmed-$REV/server/bootstrap/update_db-v1_v2.conf "\
"./GNUmed-$REV/server/bootstrap/update_db-v1_v2.sh "\
"./GNUmed-$REV/server/sql/gmappoint.sql "\
"./GNUmed-$REV/server/sql/gmmodule.sql "\
"./GNUmed-$REV/server/sql/gmrecalls.sql "\
"./GNUmed-$REV/server/sql/update_db-v1_v2.sql "\
"./GNUmed-$REV/server/sql/gmCrossDB_FKs.sql "\
"./GNUmed-$REV/server/sql/gmCrossDB_FK-views.sql "\
"./GNUmed-$REV/server/sql/gmFormDefs.sql "\
"./GNUmed-$REV/server/sql/gmPhraseWheelTest.sql "\
"./GNUmed-$REV/server/sql/ "\
"./GNUmed-$REV/server/sql/ "\
"./GNUmed-$REV/server/sql/ "\
"./GNUmed-$REV/server/sql/ "\
"./GNUmed-$REV/server/sql/ "\


echo "cleaning up"
rm -R ./GNUmed-$REV/
rm -vf $CLIENTARCH
rm -vf $SRVARCH
cd ../../../
./remove_pyc.sh
cd -


# create client package
echo "____________"
echo "=> client <="
echo "============"


# client
mkdir -p ./GNUmed-$REV/client/
cp -R ../../client/__init__.py ./GNUmed-$REV/client/
cp -R ../../client/gm-0_2.conf ./GNUmed-$REV/client/
cp -R ../../client/gm-0_2-from-cvs.sh ./GNUmed-$REV/client/
cp -R ./gnumed ./GNUmed-$REV/client/
cp -R ../../client/sitecustomize.py ./GNUmed-$REV/client/
cp -R ../../../check-prerequisites.* ./GNUmed-$REV/client/
cp -R ../../../GnuPublicLicense.txt ./GNUmed-$REV/client/


# bitmaps
mkdir -p ./GNUmed-$REV/client/bitmaps/
cp -R ./gnumed.xpm ./GNUmed-$REV/client/bitmaps/
cp -R ../../client/bitmaps/gnumedlogo.png ./GNUmed-$REV/client/bitmaps/
cp -R ../../client/bitmaps/empty-face-in-bust.png ./GNUmed-$REV/client/bitmaps/
cp -R ../../client/bitmaps/serpent.png ./GNUmed-$REV/client/bitmaps/
chmod -cR -x ./GNUmed-$REV/client/bitmaps/*.*


# business
mkdir -p ./GNUmed-$REV/client/business/
cp -R ../../client/business/*.py ./GNUmed-$REV/client/business/


# connectors
mkdir -p ./GNUmed-$REV/client/connectors/
cp -R ../../client/connectors/xdt2gnumed.* ./GNUmed-$REV/client/connectors/


# doc
mkdir -p ./GNUmed-$REV/client/doc/
cp -R ../../client/doc/gnumed.conf.example ./GNUmed-$REV/client/doc/
cp -R ../../client/doc/man-pages/gnumed.1 ./GNUmed-$REV/client/doc/gnumed.1


# exporters
mkdir -p ./GNUmed-$REV/client/exporters/
cp -R ../../client/exporters/__init__.py ./GNUmed-$REV/client/exporters
cp -R ../../client/exporters/gmPatientExporter.py ./GNUmed-$REV/client/exporters


# locale
mkdir -p ./GNUmed-$REV/client/locale/
cp -R ../../client/locale/de.po ./GNUmed-$REV/client/locale
cp -R ../../client/locale/es.po ./GNUmed-$REV/client/locale
cp -R ../../client/locale/fr.po ./GNUmed-$REV/client/locale

cd ../../client/locale/
./create-gnumed_mo.sh de
./create-gnumed_mo.sh es
./create-gnumed_mo.sh fr
cd -

cp -R ../../client/locale/de-gnumed.mo ./GNUmed-$REV/client/locale
cp -R ../../client/locale/es-gnumed.mo ./GNUmed-$REV/client/locale
cp -R ../../client/locale/fr-gnumed.mo ./GNUmed-$REV/client/locale


# pycommon
mkdir -p ./GNUmed-$REV/client/pycommon/
cp -R ../../client/pycommon/*.py ./GNUmed-$REV/client/pycommon/


# wxGladeWidgets
mkdir -p ./GNUmed-$REV/client/wxGladeWidgets/
cp -R ../../client/wxGladeWidgets/*.py ./GNUmed-$REV/client/wxGladeWidgets/
chmod -cR -x ./GNUmed-$REV/client/wxGladeWidgets/*.*


# wxpython
mkdir -p ./GNUmed-$REV/client/wxpython/
cp -R ../../client/wxpython/*.py ./GNUmed-$REV/client/wxpython/
mkdir -p ./GNUmed-$REV/client/wxpython/gui/
cp -R ../../client/wxpython/gui/*.py ./GNUmed-$REV/client/wxpython/gui/
chmod -cR -x ./GNUmed-$REV/client/wxpython/*.*
chmod -cR -x ./GNUmed-$REV/client/wxpython/gui/*.*


# pick up current User Manual
echo "picking up GNUmed User Manual from the web"
mkdir -p ./GNUmed-$REV/client/doc/user-manual/
wget -v http://wiki.gnumed.de/bin/view/Gnumed/PublishManual
rm -vf PublishManual*
wget -v -O ./GNUmed-$REV/client/doc/user-manual/GNUmed-User-Manual.tgz http://wiki.gnumed.de/twiki/gm-manual//Gnumed.tgz
cd ./GNUmed-$REV/client/doc/user-manual/
tar -xvzf GNUmed-User-Manual.tgz
ln -s Release-02.html index.html
rm -vf GNUmed-User-Manual.tgz
cd -


#----------------------------------
# create server package
echo "____________"
echo "=> server <="
echo "============"


# client
mkdir -p ./GNUmed-$REV/server
cp -R ../../../GnuPublicLicense.txt ./GNUmed-$REV/server/


# pycommon
mkdir -p ./GNUmed-$REV/server/pycommon
cp -R ../../client/pycommon/*.py ./GNUmed-$REV/server/pycommon/


# bootstrap
mkdir -p ./GNUmed-$REV/server/bootstrap
cp -R ../../server/bootstrap/* ./GNUmed-$REV/server/bootstrap/


# sql
mkdir -p ./GNUmed-$REV/server/sql
cp -R ../../server/sql/*.sql ./GNUmed-$REV/server/sql/
mkdir -p ./GNUmed-$REV/server/sql/country.specific
mkdir -p ./GNUmed-$REV/server/sql/country.specific/au
cp -R ../../server/sql/country.specific/au/*.sql ./GNUmed-$REV/server/sql/country.specific/au
mkdir -p ./GNUmed-$REV/server/sql/country.specific/ca
cp -R ../../server/sql/country.specific/ca/*.sql ./GNUmed-$REV/server/sql/country.specific/ca
mkdir -p ./GNUmed-$REV/server/sql/country.specific/de
cp -R ../../server/sql/country.specific/de/*.sql ./GNUmed-$REV/server/sql/country.specific/de
mkdir -p ./GNUmed-$REV/server/sql/country.specific/es
cp -R ../../server/sql/country.specific/es/*.sql ./GNUmed-$REV/server/sql/country.specific/es
mkdir -p ./GNUmed-$REV/server/sql/test-data
cp -R ../../server/sql/test-data/*.sql ./GNUmed-$REV/server/sql/test-data


#----------------------------------
# weed out unnecessary stuff
for fname in $FILES_REMOVE ; do
	rm -vf $fname
done ;


echo "cleaning out debris"
find ./ -name '*.pyc' -exec rm -v '{}' ';'
find ./ -name '*.log' -exec rm -v '{}' ';'
find ./GNUmed-$REV/ -name 'CVS' -type d -exec rm -v -r '{}' ';'
find ./GNUmed-$REV/ -name 'wxg' -type d -exec rm -v -r '{}' ';'


# now make tarballs
tar -cvhzf $CLIENTARCH ./GNUmed-$REV/client/
tar -cvhzf $SRVARCH ./GNUmed-$REV/server/


# cleanup
rm -R ./GNUmed-$REV/

#------------------------------------------
# $Log: make-release_tarball.sh,v $
# Revision 1.15.2.1  2006-08-15 21:15:34  ncq
# - finally build server packages, too
#
# Revision 1.15  2006/08/08 14:04:38  ncq
# - include xdt connector
#
# Revision 1.14  2006/08/07 07:16:23  ncq
# - properly call remove_pyc.sh
#
# Revision 1.13  2006/08/04 06:14:00  ncq
# - fix missing /gui/ part in deletion filenames as well as copy
#
# Revision 1.12  2006/07/30 18:01:19  ncq
# - fix rights
#
# Revision 1.11  2006/07/30 17:10:47  ncq
# - improve by Debian suggestions
#
# Revision 1.10  2006/07/26 10:36:55  ncq
# - move gnumed.xpm to more proper location
#
# Revision 1.9  2006/07/25 07:35:57  ncq
# - move user-manual into doc/
#
# Revision 1.8  2006/07/24 20:04:43  ncq
# - we do not need the bmi calculator png
#
# Revision 1.7  2006/07/23 20:39:50  ncq
# - more cleanup
#
# Revision 1.6  2006/07/22 12:49:26  ncq
# - don't need bmi for now
#
# Revision 1.5  2006/07/21 15:56:14  ncq
# - add User Manual
#
# Revision 1.4  2006/07/21 12:59:16  ncq
# - do not produce *.orig.tar.gz
#
# Revision 1.3  2006/07/19 22:10:14  ncq
# - properly clean up
#
# Revision 1.2  2006/07/19 20:03:35  ncq
# - improved client packages
#
# Revision 1.1  2006/07/19 11:31:17  ncq
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
