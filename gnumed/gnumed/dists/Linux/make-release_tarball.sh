#!/bin/bash

#====================================================
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/dists/Linux/make-release_tarball.sh,v $
# $Id: make-release_tarball.sh,v 1.96 2010-01-31 18:22:09 ncq Exp $
# license: GPL
#====================================================
CLIENTREV="0.7.rc1"
CLIENTREV="CVS-HEAD"
CLIENTARCH="gnumed-client.$CLIENTREV.tgz"

SRVREV="13.rc1"
SRVREV="CVS-HEAD"
SRVARCH="gnumed-server.$SRVREV.tgz"

FILES_REMOVE=\
"./gnumed-client.$CLIENTREV/client/business/README "\
"./gnumed-client.$CLIENTREV/client/business/gmOrganization.py "\
"./gnumed-client.$CLIENTREV/client/business/gmXmlDocDesc.py "\
"./gnumed-client.$CLIENTREV/client/pycommon/gmDrugObject.py "\
"./gnumed-client.$CLIENTREV/client/pycommon/gmDrugView.py "\
"./gnumed-client.$CLIENTREV/client/pycommon/gmSchemaRevisionCheck.py "\
"./gnumed-client.$CLIENTREV/client/pycommon/gmSerialTools.py "\
"./gnumed-client.$CLIENTREV/client/pycommon/gmTrace.py "\
"./gnumed-client.$CLIENTREV/client/pycommon/gmdbf.py "\
"./gnumed-client.$CLIENTREV/client/pycommon/gmCLI.py "\
"./gnumed-client.$CLIENTREV/client/pycommon/gmPG.py "\
"./gnumed-client.$CLIENTREV/server/business/README "\
"./gnumed-client.$CLIENTREV/server/business/gmOrganization.py "\
"./gnumed-client.$CLIENTREV/server/business/gmXmlDocDesc.py "\
"./gnumed-client.$CLIENTREV/server/pycommon/gmDrugObject.py "\
"./gnumed-client.$CLIENTREV/server/pycommon/gmDrugView.py "\
"./gnumed-client.$CLIENTREV/server/pycommon/gmSchemaRevisionCheck.py "\
"./gnumed-client.$CLIENTREV/server/pycommon/gmSerialTools.py "\
"./gnumed-client.$CLIENTREV/server/pycommon/gmTrace.py "\
"./gnumed-client.$CLIENTREV/server/pycommon/gmdbf.py "\
"./gnumed-client.$CLIENTREV/server/pycommon/gmPG.py "\
"./gnumed-client.$CLIENTREV/server/bootstrap/README "\
"./gnumed-client.$CLIENTREV/client/wxGladeWidgets/README "\
"./gnumed-client.$CLIENTREV/client/wxGladeWidgets/wxgAU_AdminLoginV01.py "\
"./gnumed-client.$CLIENTREV/client/wxGladeWidgets/wxgAU_DBUserSetupV01.py "\
"./gnumed-client.$CLIENTREV/client/wxGladeWidgets/wxgAU_StaffMgrPanel.py "\
"./gnumed-client.$CLIENTREV/client/wxGladeWidgets/wxgAU_StaffV01.py "\
"./gnumed-client.$CLIENTREV/client/wxGladeWidgets/wxgRequest.py "\
"./gnumed-client.$CLIENTREV/client/wxGladeWidgets/wxgDoubleListSplitterPnl.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/StyledTextCtrl_1.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gmDermTool.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gmProgressNoteSTC.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/zz-gmNewFileTemplate.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gmAU_VaccV01.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gmBMIWidgets.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gmCharacterValidator.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gmCryptoText.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gmFormPrinter.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gmGP_ActiveProblems.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gmGP_FamilyHistorySummary.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gmGP_HabitsRiskFactors.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gmGP_Inbox.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gmGP_PatientPicture.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gmGP_SocialHistory.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gmLabWidgets.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gmListCtrlMapper.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gmMultiColumnList.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gmMultiSash.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gmPatientHolder.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gmPlugin_Patient.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gmPregWidgets.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gmSelectPerson.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gmShadow.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gmSQLListControl.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gmSQLSimpleSearch.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gui/gmAllergiesPlugin.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gui/gmAU_VaccV01Plugin.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gui/gmClinicalWindowManager.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gui/gmContacts.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gui/gmConfigRegistry.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gui/gmDemographicsEditor.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gui/gmDrugDisplay.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gui/gmEMRTextDumpPlugin.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gui/gmGuidelines.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gui/gmLabJournal.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gui/gmManual.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gui/gmMultiSashedProgressNoteInputPlugin.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gui/gmOffice.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gui/gmPython.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gui/gmRequest.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gui/gmShowLab.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gui/gmSQL.py "\
"./gnumed-client.$CLIENTREV/client/wxpython/gui/gmVaccinationsPlugin.py "\
"./gnumed-client.$CLIENTREV/server/bootstrap/xxx-upgrade-instructions.txt "\
"./gnumed-client.$CLIENTREV/server/bootstrap/amis-config.set "\
"./gnumed-client.$CLIENTREV/server/bootstrap/bootstrap-amis.conf "\
"./gnumed-client.$CLIENTREV/server/bootstrap/bootstrap-archive.conf "\
"./gnumed-client.$CLIENTREV/server/bootstrap/install_AMIS_data.sh "\
"./gnumed-client.$CLIENTREV/server/bootstrap/redo-max.sh "\
"./gnumed-client.$CLIENTREV/server/bootstrap/update_db-v1_v2.conf "\
"./gnumed-client.$CLIENTREV/server/bootstrap/update_db-v1_v2.sh "\
"./gnumed-client.$CLIENTREV/server/sql/gmappoint.sql "\
"./gnumed-client.$CLIENTREV/server/sql/gmmodule.sql "\
"./gnumed-client.$CLIENTREV/server/sql/gmrecalls.sql "\
"./gnumed-client.$CLIENTREV/server/sql/update_db-v1_v2.sql "\
"./gnumed-client.$CLIENTREV/server/sql/gmCrossDB_FKs.sql "\
"./gnumed-client.$CLIENTREV/server/sql/gmCrossDB_FK-views.sql "\
"./gnumed-client.$CLIENTREV/server/sql/gmFormDefs.sql "\
"./gnumed-client.$CLIENTREV/server/sql/gmPhraseWheelTest.sql "\
"./gnumed-client.$CLIENTREV/server/sql/test-data/BC-Excelleris-test_patients.sql "


echo "cleaning up"
rm -R ./gnumed-client.$CLIENTREV/
rm -vf $CLIENTARCH
rm -vf $SRVARCH
cd ../../../
./remove_pyc.sh
cd -


# create client package
echo "____________"
echo "=> client <="
echo "============"


# external tools
mkdir -p ./gnumed-client.$CLIENTREV/external-tools/
cp -R ../../external-tools/gm-install_arriba ./gnumed-client.$CLIENTREV/external-tools/
cp -R ../../external-tools/gm-download_loinc ./gnumed-client.$CLIENTREV/external-tools/
cp -R ../../external-tools/gm-download_atc ./gnumed-client.$CLIENTREV/external-tools/
cp -R ../../external-tools/gm-print_doc ./gnumed-client.$CLIENTREV/external-tools/
cp -R ../../external-tools/gm-read_chipcard.sh ./gnumed-client.$CLIENTREV/external-tools/
cp -R ../../external-tools/gnumed-client-init_script.sh ./gnumed-client.$CLIENTREV/external-tools/
cp -R ../../external-tools/gm-remove_person.sh ./gnumed-client.$CLIENTREV/external-tools/
cp -R ../../external-tools/gm-install_client_locally.sh ./gnumed-client.$CLIENTREV/external-tools/


# client
mkdir -p ./gnumed-client.$CLIENTREV/client/
cp -R ../../client/__init__.py ./gnumed-client.$CLIENTREV/client/
cp -R ../../client/gm-from-cvs.conf ./gnumed-client.$CLIENTREV/client/
cp -R ../../client/gm-from-cvs.sh ./gnumed-client.$CLIENTREV/client/
cp -R ../../client/gm-from-cvs.bat ./gnumed-client.$CLIENTREV/client/
cp -R ./gnumed ./gnumed-client.$CLIENTREV/client/
cp -R ./gnumed-client.desktop ./gnumed-client.$CLIENTREV/client/
cp -R ../../client/sitecustomize.py ./gnumed-client.$CLIENTREV/client/
cp -R ../../../check-prerequisites.* ./gnumed-client.$CLIENTREV/client/
cp -R ../../../GnuPublicLicense.txt ./gnumed-client.$CLIENTREV/client/


# bitmaps
mkdir -p ./gnumed-client.$CLIENTREV/client/bitmaps/
cp -R ./gnumed.xpm ./gnumed-client.$CLIENTREV/client/bitmaps/
cp -R ../../client/bitmaps/gnumedlogo.png ./gnumed-client.$CLIENTREV/client/bitmaps/
cp -R ../../client/bitmaps/empty-face-in-bust.png ./gnumed-client.$CLIENTREV/client/bitmaps/
cp -R ../../client/bitmaps/serpent.png ./gnumed-client.$CLIENTREV/client/bitmaps/
chmod -cR -x ./gnumed-client.$CLIENTREV/client/bitmaps/*.*


# business
mkdir -p ./gnumed-client.$CLIENTREV/client/business/
cp -R ../../client/business/*.py ./gnumed-client.$CLIENTREV/client/business/


# connectors
mkdir -p ./gnumed-client.$CLIENTREV/client/connectors/
cp -R ../../client/connectors/gm_ctl_client.* ./gnumed-client.$CLIENTREV/client/connectors/


# doc
mkdir -p ./gnumed-client.$CLIENTREV/client/doc/
cp -R ../../client/gm-from-cvs.conf ./gnumed-client.$CLIENTREV/client/doc/gnumed.conf.example
cp -R ../../client/doc/hook_script_example.py ./gnumed-client.$CLIENTREV/client/doc/hook_script_example.py
cp -R ../../client/doc/man-pages/gnumed.1 ./gnumed-client.$CLIENTREV/client/doc/gnumed.1
cp -R ../../client/doc/man-pages/gm-print_doc.1 ./gnumed-client.$CLIENTREV/client/doc/gm-print_doc.1
cp -R ../../client/doc/man-pages/gm_ctl_client.1 ./gnumed-client.$CLIENTREV/client/doc/gm_ctl_client.1
cp -R ../../client/doc/man-pages/gm-install_arriba.8 ./gnumed-client.$CLIENTREV/client/doc/gm-install_arriba.8


# etc
mkdir -p ./gnumed-client.$CLIENTREV/client/etc/gnumed/
cp -R ../../client/gm-from-cvs.conf ./gnumed-client.$CLIENTREV/client/etc/gnumed/gnumed-client.conf.example
cp -R ../../client/etc/gnumed/mime_type2file_extension.conf.example ./gnumed-client.$CLIENTREV/client/etc/gnumed/
cp -R ../../client/etc/gnumed/egk+kvk-demon.conf.example ./gnumed-client.$CLIENTREV/client/etc/gnumed/


# exporters
mkdir -p ./gnumed-client.$CLIENTREV/client/exporters/
cp -R ../../client/exporters/__init__.py ./gnumed-client.$CLIENTREV/client/exporters
cp -R ../../client/exporters/gmPatientExporter.py ./gnumed-client.$CLIENTREV/client/exporters


# locale
mkdir -p ./gnumed-client.$CLIENTREV/client/locale/
cp -R ../../client/locale/de.po ./gnumed-client.$CLIENTREV/client/locale
cp -R ../../client/locale/es.po ./gnumed-client.$CLIENTREV/client/locale
cp -R ../../client/locale/fr.po ./gnumed-client.$CLIENTREV/client/locale
cp -R ../../client/locale/it.po ./gnumed-client.$CLIENTREV/client/locale
cp -R ../../client/locale/nb.po ./gnumed-client.$CLIENTREV/client/locale
cp -R ../../client/locale/nl.po ./gnumed-client.$CLIENTREV/client/locale
cp -R ../../client/locale/pl.po ./gnumed-client.$CLIENTREV/client/locale
cp -R ../../client/locale/pt_BR.po ./gnumed-client.$CLIENTREV/client/locale
cp -R ../../client/locale/ru.po ./gnumed-client.$CLIENTREV/client/locale

cd ../../client/locale/
./create-gnumed_mo.sh de
./create-gnumed_mo.sh es
./create-gnumed_mo.sh fr
./create-gnumed_mo.sh it
./create-gnumed_mo.sh nb
./create-gnumed_mo.sh nl
./create-gnumed_mo.sh pl
./create-gnumed_mo.sh pt_BR
./create-gnumed_mo.sh ru
cd -

cp -R ../../client/locale/de-gnumed.mo ./gnumed-client.$CLIENTREV/client/locale
cp -R ../../client/locale/es-gnumed.mo ./gnumed-client.$CLIENTREV/client/locale
cp -R ../../client/locale/fr-gnumed.mo ./gnumed-client.$CLIENTREV/client/locale
cp -R ../../client/locale/it-gnumed.mo ./gnumed-client.$CLIENTREV/client/locale
cp -R ../../client/locale/nb-gnumed.mo ./gnumed-client.$CLIENTREV/client/locale
cp -R ../../client/locale/nl-gnumed.mo ./gnumed-client.$CLIENTREV/client/locale
cp -R ../../client/locale/pl-gnumed.mo ./gnumed-client.$CLIENTREV/client/locale
cp -R ../../client/locale/pt_BR-gnumed.mo ./gnumed-client.$CLIENTREV/client/locale
cp -R ../../client/locale/ru-gnumed.mo ./gnumed-client.$CLIENTREV/client/locale


# pycommon
mkdir -p ./gnumed-client.$CLIENTREV/client/pycommon/
cp -R ../../client/pycommon/*.py ./gnumed-client.$CLIENTREV/client/pycommon/


# wxGladeWidgets
mkdir -p ./gnumed-client.$CLIENTREV/client/wxGladeWidgets/
cp -R ../../client/wxGladeWidgets/*.py ./gnumed-client.$CLIENTREV/client/wxGladeWidgets/
chmod -cR -x ./gnumed-client.$CLIENTREV/client/wxGladeWidgets/*.*


# wxpython
mkdir -p ./gnumed-client.$CLIENTREV/client/wxpython/
cp -R ../../client/wxpython/*.py ./gnumed-client.$CLIENTREV/client/wxpython/
mkdir -p ./gnumed-client.$CLIENTREV/client/wxpython/gui/
cp -R ../../client/wxpython/gui/*.py ./gnumed-client.$CLIENTREV/client/wxpython/gui/
chmod -cR -x ./gnumed-client.$CLIENTREV/client/wxpython/*.*
chmod -cR -x ./gnumed-client.$CLIENTREV/client/wxpython/gui/*.*


# current User Manual
echo "picking up GNUmed User Manual from the web"
mkdir -p ./gnumed-client.$CLIENTREV/client/doc/user-manual/
wget -v http://wiki.gnumed.de/bin/view/Gnumed/PublishManual		#http://wiki.gnumed.de/bin/publish/Gnumed
rm -vf PublishManual*
wget -v -O ./gnumed-client.$CLIENTREV/client/doc/user-manual/GNUmed-User-Manual.zip http://wiki.gnumed.de/pub/Gnumed.zip
cd ./gnumed-client.$CLIENTREV/client/doc/user-manual/
unzip GNUmed-User-Manual.zip
#tar -xvzf GNUmed-User-Manual.tgz
rm -vf Release-02.html
ln -s GnumedManual.html index.html
#rm -vf GNUmed-User-Manual.tgz
rm -vf GNUmed-User-Manual.zip
cd -


# current API documentation
echo "downloading the API documentation"
mkdir -p ./gnumed-client.$CLIENTREV/client/doc/api/
cd ./gnumed-client.$CLIENTREV/client/doc/api/
wget -v -r -k -np -nd http://salaam.homeunix.com/~ncq/gnumed/api/
cd -


# current schema documentation
echo "downloading SQL schema documentation"
mkdir -p ./gnumed-client.$CLIENTREV/client/doc/schema/
cd ./gnumed-client.$CLIENTREV/client/doc/schema/
wget -v -r -k -np -nd http://salaam.homeunix.com/~ncq/gnumed/schema/release/gnumed-schema.html
wget -v -r -k -np -nd http://salaam.homeunix.com/~ncq/gnumed/schema/release/gnumed-schema-no_audit.dot
cd -


#----------------------------------
# create server package
echo "____________"
echo "=> server <="
echo "============"


# scripts
mkdir -p ./gnumed-client.$CLIENTREV/server
cp -R ../../../GnuPublicLicense.txt ./gnumed-client.$CLIENTREV/server/

cp -R ../../server/gm-bootstrap_server ./gnumed-client.$CLIENTREV/server/
cp -R ../../server/gm-upgrade_server ./gnumed-client.$CLIENTREV/server/
cp -R ../../server/gm-fixup_server ./gnumed-client.$CLIENTREV/server/
cp -R ../../server/gm-adjust_db_settings.sh ./gnumed-client.$CLIENTREV/server/

cp -R ../../server/gm-backup_database.sh ./gnumed-client.$CLIENTREV/server/
cp -R ../../server/gm-restore_database.sh ./gnumed-client.$CLIENTREV/server/

cp -R ../../server/gm-backup_data.sh ./gnumed-client.$CLIENTREV/server/
cp -R ../../server/gm-restore_data.sh ./gnumed-client.$CLIENTREV/server/

cp -R ../../server/gm-zip+sign_backups.sh ./gnumed-client.$CLIENTREV/server/
cp -R ../../server/gm-move_backups_offsite.sh ./gnumed-client.$CLIENTREV/server/

cp -R ../../external-tools/gm-remove_person.sh ./gnumed-client.$CLIENTREV/server/

cp -R ../../client/__init__.py ./gnumed-client.$CLIENTREV/server/


# pycommon
mkdir -p ./gnumed-client.$CLIENTREV/server/pycommon
cp -R ../../client/pycommon/*.py ./gnumed-client.$CLIENTREV/server/pycommon/


# bootstrap
mkdir -p ./gnumed-client.$CLIENTREV/server/bootstrap
cp -R ../../server/bootstrap/* ./gnumed-client.$CLIENTREV/server/bootstrap/


# doc
mkdir -p ./gnumed-client.$CLIENTREV/server/doc/schema
cp -R ../../server/bootstrap/README ./gnumed-client.$CLIENTREV/server/doc/
cp -R ../../client/doc/man-pages/gm-bootstrap_server.8 ./gnumed-client.$CLIENTREV/server/doc/
cp -R ../../client/doc/man-pages/gm-upgrade_server.8 ./gnumed-client.$CLIENTREV/server/doc/
cp -R ../../client/doc/man-pages/gm-fixup_server.8 ./gnumed-client.$CLIENTREV/server/doc/
cp -R ./gnumed-client.$CLIENTREV/client/doc/schema/ ./gnumed-client.$CLIENTREV/server/doc/


# etc
mkdir -p ./gnumed-client.$CLIENTREV/server/etc/gnumed/
cp -R ../../client/etc/gnumed/gnumed-backup.conf.example ./gnumed-client.$CLIENTREV/server/etc/gnumed/
cp -R ../../client/etc/gnumed/gnumed-restore.conf.example ./gnumed-client.$CLIENTREV/server/etc/gnumed/


# sql
mkdir -p ./gnumed-client.$CLIENTREV/server/sql
cp -R ../../server/sql/*.sql ./gnumed-client.$CLIENTREV/server/sql/
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/country.specific
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/country.specific/au
cp -R ../../server/sql/country.specific/au/*.sql ./gnumed-client.$CLIENTREV/server/sql/country.specific/au
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/country.specific/ca
cp -R ../../server/sql/country.specific/ca/*.sql ./gnumed-client.$CLIENTREV/server/sql/country.specific/ca
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/country.specific/de
cp -R ../../server/sql/country.specific/de/*.sql ./gnumed-client.$CLIENTREV/server/sql/country.specific/de
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/country.specific/es
cp -R ../../server/sql/country.specific/es/*.sql ./gnumed-client.$CLIENTREV/server/sql/country.specific/es
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/test-data
cp -R ../../server/sql/test-data/*.sql ./gnumed-client.$CLIENTREV/server/sql/test-data

mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v2-v3
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v2-v3/dynamic
cp -R ../../server/sql/v2-v3/dynamic/*.sql ./gnumed-client.$CLIENTREV/server/sql/v2-v3/dynamic
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v2-v3/static
cp -R ../../server/sql/v2-v3/static/*.sql ./gnumed-client.$CLIENTREV/server/sql/v2-v3/static
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v2-v3/superuser
cp -R ../../server/sql/v2-v3/superuser/*.sql ./gnumed-client.$CLIENTREV/server/sql/v2-v3/superuser

mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v3-v4
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v3-v4/dynamic
cp -R ../../server/sql/v3-v4/dynamic/*.sql ./gnumed-client.$CLIENTREV/server/sql/v3-v4/dynamic
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v3-v4/static
cp -R ../../server/sql/v3-v4/static/*.sql ./gnumed-client.$CLIENTREV/server/sql/v3-v4/static
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v3-v4/superuser
cp -R ../../server/sql/v3-v4/superuser/*.sql ./gnumed-client.$CLIENTREV/server/sql/v3-v4/superuser

mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v4-v5
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v4-v5/dynamic
cp -R ../../server/sql/v4-v5/dynamic/*.sql ./gnumed-client.$CLIENTREV/server/sql/v4-v5/dynamic
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v4-v5/static
cp -R ../../server/sql/v4-v5/static/*.sql ./gnumed-client.$CLIENTREV/server/sql/v4-v5/static
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v4-v5/superuser
cp -R ../../server/sql/v4-v5/superuser/*.sql ./gnumed-client.$CLIENTREV/server/sql/v4-v5/superuser

mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v5-v6
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v5-v6/dynamic
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v5-v6/static

cp -R ../../server/sql/v5-v6/dynamic/*.sql ./gnumed-client.$CLIENTREV/server/sql/v5-v6/dynamic
cp -R ../../server/sql/v5-v6/static/*.sql ./gnumed-client.$CLIENTREV/server/sql/v5-v6/static


mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v6-v7
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v6-v7/dynamic
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v6-v7/static
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v6-v7/data
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v6-v7/python

cp -R ../../server/sql/v6-v7/dynamic/*.sql ./gnumed-client.$CLIENTREV/server/sql/v6-v7/dynamic
cp -R ../../server/sql/v6-v7/static/*.sql ./gnumed-client.$CLIENTREV/server/sql/v6-v7/static
cp -R ../../server/sql/v6-v7/data/* ./gnumed-client.$CLIENTREV/server/sql/v6-v7/data
cp -R ../../server/sql/v6-v7/python/*.py ./gnumed-client.$CLIENTREV/server/sql/v6-v7/python


mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v7-v8
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v7-v8/dynamic
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v7-v8/static

cp -R ../../server/sql/v7-v8/dynamic/*.sql ./gnumed-client.$CLIENTREV/server/sql/v7-v8/dynamic
cp -R ../../server/sql/v7-v8/static/*.sql ./gnumed-client.$CLIENTREV/server/sql/v7-v8/static


mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v8-v9
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v8-v9/dynamic
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v8-v9/static

cp -R ../../server/sql/v8-v9/dynamic/*.sql ./gnumed-client.$CLIENTREV/server/sql/v8-v9/dynamic
cp -R ../../server/sql/v8-v9/static/*.sql ./gnumed-client.$CLIENTREV/server/sql/v8-v9/static


mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v9-v10
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v9-v10/dynamic
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v9-v10/static
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v9-v10/superuser
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v9-v10/fixups

cp -R ../../server/sql/v9-v10/dynamic/*.sql ./gnumed-client.$CLIENTREV/server/sql/v9-v10/dynamic
cp -R ../../server/sql/v9-v10/static/*.sql ./gnumed-client.$CLIENTREV/server/sql/v9-v10/static
cp -R ../../server/sql/v9-v10/superuser/*.sql ./gnumed-client.$CLIENTREV/server/sql/v9-v10/superuser
cp -R ../../server/sql/v9-v10/fixups/*.sql ./gnumed-client.$CLIENTREV/server/sql/v9-v10/fixups


mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v10-v11
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v10-v11/dynamic
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v10-v11/static
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v10-v11/superuser
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v10-v11/fixups

cp -R ../../server/sql/v10-v11/dynamic/*.sql ./gnumed-client.$CLIENTREV/server/sql/v10-v11/dynamic
cp -R ../../server/sql/v10-v11/static/*.sql ./gnumed-client.$CLIENTREV/server/sql/v10-v11/static
cp -R ../../server/sql/v10-v11/superuser/*.sql ./gnumed-client.$CLIENTREV/server/sql/v10-v11/superuser
cp -R ../../server/sql/v10-v11/fixups/*.sql ./gnumed-client.$CLIENTREV/server/sql/v10-v11/fixups


mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v11-v12
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v11-v12/dynamic
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v11-v12/static
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v11-v12/superuser
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v11-v12/data
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v11-v12/python
#mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v11-v12/fixups

cp -R ../../server/sql/v11-v12/dynamic/*.sql ./gnumed-client.$CLIENTREV/server/sql/v11-v12/dynamic
cp -R ../../server/sql/v11-v12/static/*.sql ./gnumed-client.$CLIENTREV/server/sql/v11-v12/static
cp -R ../../server/sql/v11-v12/superuser/*.sql ./gnumed-client.$CLIENTREV/server/sql/v11-v12/superuser
cp -R ../../server/sql/v11-v12/data/* ./gnumed-client.$CLIENTREV/server/sql/v11-v12/data
cp -R ../../server/sql/v11-v12/python/*.py ./gnumed-client.$CLIENTREV/server/sql/v11-v12/python
#cp -R ../../server/sql/v11-v12/fixups/*.sql ./gnumed-client.$CLIENTREV/server/sql/v11-v12/fixups


#----------------------------------
# weed out unnecessary stuff
for fname in $FILES_REMOVE ; do
	rm -f $fname
done ;


echo "cleaning out debris"
find ./ -name '*.pyc' -exec rm -v '{}' ';'
find ./ -name '*.log' -exec rm -v '{}' ';'
find ./gnumed-client.$CLIENTREV/ -name 'CVS' -type d -exec rm -v -r '{}' ';'
find ./gnumed-client.$CLIENTREV/ -name 'wxg' -type d -exec rm -v -r '{}' ';'


# now make tarballs
# - client
cd gnumed-client.$CLIENTREV
ln -s client Gnumed
cd ..
tar -czf $CLIENTARCH ./gnumed-client.$CLIENTREV/client/ ./gnumed-client.$CLIENTREV/external-tools/ ./gnumed-client.$CLIENTREV/Gnumed
# - server
mv gnumed-client.$CLIENTREV gnumed-server.$SRVREV
cd gnumed-server.$SRVREV
rm Gnumed
ln -s server Gnumed
cd ..
tar -czf $SRVARCH ./gnumed-server.$SRVREV/server/ ./gnumed-server.$SRVREV/Gnumed


# cleanup
rm -R ./gnumed-server.$SRVREV/

echo "include schema docs"

#------------------------------------------
# $Log: make-release_tarball.sh,v $
# Revision 1.96  2010-01-31 18:22:09  ncq
# - include pt_BR
#
# Revision 1.95  2010/01/21 09:01:20  ncq
# - bump version
#
# Revision 1.94  2010/01/19 15:46:37  ncq
# - include more languages
#
# Revision 1.93  2010/01/15 13:33:34  ncq
# - bump version
#
# Revision 1.92  2010/01/09 19:35:25  ncq
# - bump version
# - include v12 data/python
#
# Revision 1.91  2009/12/26 11:54:40  ncq
# - bump version
#
# Revision 1.90  2009/12/25 22:10:52  ncq
# - include man page for new gm-print_doc
#
# Revision 1.89  2009/12/01 22:07:00  ncq
# - bump version
#
# Revision 1.88  2009/11/24 21:04:19  ncq
# - remove person now in external tools
#
# Revision 1.87  2009/11/18 16:12:24  ncq
# - add API/schema docs to tarball as per David Merz' suggestion
#
# Revision 1.86  2009/11/13 21:08:55  ncq
# - include Polish
#
# Revision 1.85  2009/09/17 21:57:58  ncq
# - cleanup manual zip file
# - include v11 fixups
#
# Revision 1.84  2009/09/13 18:47:19  ncq
# - local client installer now in external tools
#
# Revision 1.83  2009/09/08 17:17:55  ncq
# - lowercase and adjust tarball names as per list discussion
#
# Revision 1.82  2009/08/24 20:11:27  ncq
# - bump db version
# - fix tag creation
# - provider inbox:
# 	enable filter-to-active-patient,
# 	listen to new signal,
# 	use cInboxMessage class
# - properly constrain LOINC phrasewheel SQL
# - include v12 scripts in release
# - install arriba jar to /usr/local/bin/
# - check for table existence in audit schema generator
# - include dem.message inbox with additional generic signals
#
# Revision 1.81  2009/08/11 11:04:28  ncq
# - version fix, prep for release
#
# Revision 1.80  2009/08/04 13:03:19  ncq
# - bump version
# - remove gmManual.py
# - copy client.conf.example from gm-from-cvs.conf
#
# Revision 1.79  2009/07/18 12:15:53  ncq
# - (0.5/v11).rc4
#
# Revision 1.78  2009/07/06 19:52:54  ncq
# - 0.5.rc3/11.rc3
#
# Revision 1.77  2009/06/22 12:40:01  ncq
# - bump versions
#
# Revision 1.76  2009/06/11 13:08:15  ncq
# - bump version
#
# Revision 1.75  2009/06/11 13:04:35  ncq
# - cleanup
#
# Revision 1.74  2009/06/10 21:03:40  ncq
# - include ATC downloader
#
# Revision 1.73  2009/06/04 16:35:03  ncq
# - include gm-download_loinc
#
# Revision 1.72  2009/05/18 15:35:52  ncq
# - include fixups 9-10
#
# Revision 1.71  2009/05/13 13:13:23  ncq
# - exclude some test data
#
# Revision 1.70  2009/05/04 11:41:01  ncq
# - include gm-fixup_server
#
# Revision 1.69  2009/04/24 12:11:08  ncq
# - include ARRIBA installer
#
# Revision 1.68  2009/04/03 11:08:48  ncq
# - include v11 upgrade scripts
#
# Revision 1.67  2009/04/03 09:53:33  ncq
# - fix manual zip location
#
# Revision 1.66  2009/03/04 13:50:25  ncq
# - bump version
#
# Revision 1.65  2009/03/02 11:24:40  ncq
# - bump version
#
# Revision 1.64  2009/02/27 12:41:27  ncq
# - bump version
#
# Revision 1.63  2009/02/25 09:56:34  ncq
# - proper path
#
# Revision 1.62  2009/02/24 18:06:03  ncq
# - include new local installer
#
# Revision 1.61  2009/02/18 16:55:45  shilbert
# - added missing file for v9 to v10 upgrade
#
# Revision 1.60  2009/02/17 12:00:09  ncq
# - bump version
#
# Revision 1.59  2009/02/05 13:05:08  ncq
# - fix typo
#
# Revision 1.58  2009/01/17 23:10:25  ncq
# - bump version
#
# Revision 1.57  2009/01/15 11:41:41  ncq
# - the user manual now is a zip file
#
# Revision 1.56  2009/01/07 12:30:48  ncq
# - fix double README in server package
# - put man pages into proper section
#
# Revision 1.55  2009/01/06 18:27:02  ncq
# - include more server side scripts and man pages
#
# Revision 1.54  2008/08/31 16:17:43  ncq
# - include gm-read_chipcard.sh
#
# Revision 1.53  2008/08/28 18:35:36  ncq
# - include scripts for KVKd startup
#
# Revision 1.52  2008/08/23 15:00:05  ncq
# - bump RC version
#
# Revision 1.51  2008/08/21 13:30:27  ncq
# - rearrange version vars
#
# Revision 1.50  2008/08/06 13:25:46  ncq
# - explicitely bash it
#
# Revision 1.49  2008/07/24 18:22:52  ncq
# - some cleaup
#
# Revision 1.48  2008/04/22 21:20:03  ncq
# - no more gmCLI
#
# Revision 1.47  2008/03/17 14:56:33  ncq
# - properly cleanup pycommon/ in server/, too
#
# Revision 1.46  2008/02/25 17:45:50  ncq
# - include Italian
#
# Revision 1.45  2008/01/16 19:40:55  ncq
# - deprecate gmConfigRegistry
# - include v8-v9 sql dirs
#
# Revision 1.44  2008/01/05 16:42:38  ncq
# - include example conf file for mime type to file extension mapping
#
# Revision 1.43  2007/12/26 18:36:35  ncq
# - delete old CLI/PG libs from tarball
#
# Revision 1.42  2007/12/06 13:08:55  ncq
# - include v7-v8/static/
#
# Revision 1.41  2007/12/02 11:43:39  ncq
# - include gm-backup_data.sh
#
# Revision 1.40  2007/10/25 12:22:04  ncq
# - include desktop file
#
# Revision 1.39  2007/10/22 12:31:53  ncq
# - include v8 stuff
#
# Revision 1.38  2007/10/19 12:53:00  ncq
# - include Snellen
#
# Revision 1.37  2007/09/24 18:40:49  ncq
# - include v7 sql scripts
# - include zip+sign script
#
# Revision 1.36  2007/08/15 09:21:21  ncq
# - we do need gmForms.py now
#
# Revision 1.35  2007/05/22 14:03:43  ncq
# - cleanup of files
#
# Revision 1.34  2007/05/08 16:07:32  ncq
# - include restore script and docs in server package
#
# Revision 1.33  2007/04/27 13:30:28  ncq
# - properly download manual again
#
# Revision 1.32  2007/04/19 13:18:46  ncq
# - cleanup
#
# Revision 1.31  2007/04/06 23:16:21  ncq
# - add v5 -> v6 schema files
#
# Revision 1.30  2007/03/31 21:52:04  ncq
# - rename client to server directory when packing tarballs
# - add cleanup
#
# Revision 1.29  2007/03/26 17:18:39  ncq
# - set CVS HEAD revision to CVS-HEAD
#
# Revision 1.28  2007/03/18 14:12:40  ncq
# - exclude some as-yet unused wxGlade widgets
#
# Revision 1.27  2007/02/19 16:45:45  ncq
# - include hook_script_example.py
#
# Revision 1.26  2007/02/17 14:02:36  ncq
# - no more STIKO browser plugin
#
# Revision 1.25  2007/02/16 15:34:53  ncq
# - include backup and offsite moving script with proper name
#
# Revision 1.24  2007/02/15 14:58:37  ncq
# - fix caps typo
#
# Revision 1.23  2007/02/04 16:18:36  ncq
# - include __init__.py in server/
# - include SQL for 3-4 und 4-5
#
# Revision 1.22  2007/01/29 13:00:01  ncq
# - include man page for gm_ctl_client.py
#
# Revision 1.21  2007/01/24 11:05:59  ncq
# - bump client rev to 0.2.next
# - bump server rev to v5
# - better name for server tgz
#
# Revision 1.20  2006/12/18 18:39:15  ncq
# - include backup script
#
# Revision 1.19  2006/12/18 15:52:38  ncq
# - port improvements from rel-0-2-patches branch
# - make it 0.2.3 now
#
# Revision 1.18  2006/08/15 08:06:39  ncq
# - better name for tgz
#
# Revision 1.17  2006/08/14 20:27:01  ncq
# - don't call it 0.2 anymore as it isn't
#
# Revision 1.16  2006/08/12 19:47:06  ncq
# - link index.html directly to GnumedManual.html
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
