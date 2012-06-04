#!/bin/bash

#====================================================
# license: GPL v2 or later
#====================================================
CLIENTREV="1.2.rc5"
CLIENTARCH="gnumed-client.$CLIENTREV.tgz"

SRVREV="17.rc5"
SRVARCH="gnumed-server.$SRVREV.tgz"

FILES_REMOVE=\
"./gnumed-client.$CLIENTREV/client/business/README "\
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
cd ../../../../
./remove-debris.sh
cd -


# create client package
echo "____________"
echo "=> client <="
echo "============"


# external tools
mkdir -p ./gnumed-client.$CLIENTREV/external-tools/
cp -R ../../external-tools/gm-install_arriba ./gnumed-client.$CLIENTREV/external-tools/
cp -R ../../external-tools/gm-download_data ./gnumed-client.$CLIENTREV/external-tools/
cp -R ../../external-tools/gm-download_atc ./gnumed-client.$CLIENTREV/external-tools/
cp -R ../../external-tools/gm-print_doc ./gnumed-client.$CLIENTREV/external-tools/
cp -R ../../external-tools/gm-read_chipcard.sh ./gnumed-client.$CLIENTREV/external-tools/
cp -R ../../external-tools/gnumed-client-init_script.sh ./gnumed-client.$CLIENTREV/external-tools/
cp -R ../../external-tools/gm-remove_person.sh ./gnumed-client.$CLIENTREV/external-tools/
cp -R ../../external-tools/gm-install_client_locally.sh ./gnumed-client.$CLIENTREV/external-tools/
cp -R ../../external-tools/check-prerequisites.* ./gnumed-client.$CLIENTREV/external-tools/


# client
mkdir -p ./gnumed-client.$CLIENTREV/client/
cp -R ../../client/__init__.py ./gnumed-client.$CLIENTREV/client/
cp -R ../../client/gnumed.py ./gnumed-client.$CLIENTREV/client/
cp -R ../../client/gm-from-vcs.conf ./gnumed-client.$CLIENTREV/client/
cp -R ../../client/gm-from-vcs.sh ./gnumed-client.$CLIENTREV/client/
cp -R ../../client/gm-from-vcs.bat ./gnumed-client.$CLIENTREV/client/
cp -R ./gnumed ./gnumed-client.$CLIENTREV/client/
cp -R ./gnumed-client.desktop ./gnumed-client.$CLIENTREV/client/
cp -R ../../client/sitecustomize.py ./gnumed-client.$CLIENTREV/client/
cp -R ../../../CHANGELOG ./gnumed-client.$CLIENTREV/client/
cp -R ../../../LICENSE ./gnumed-client.$CLIENTREV/client/
cp -R ../../../GnuPublicLicense.txt ./gnumed-client.$CLIENTREV/client/


# bitmaps
mkdir -p ./gnumed-client.$CLIENTREV/client/bitmaps/
cp -R ../../client/bitmaps/gnumedlogo.png ./gnumed-client.$CLIENTREV/client/bitmaps/
cp -R ../../client/bitmaps/empty-face-in-bust.png ./gnumed-client.$CLIENTREV/client/bitmaps/
cp -R ../../client/bitmaps/serpent.png ./gnumed-client.$CLIENTREV/client/bitmaps/
cp -R ../../client/bitmaps/gm_icon-serpent_and_gnu.png ./gnumed-client.$CLIENTREV/client/bitmaps/
cp -R ../../client/bitmaps/gm_icon-serpent_and_gnu.ico ./gnumed-client.$CLIENTREV/client/bitmaps/
cp -R ../../client/bitmaps/gm_icon-serpent_and_gnu.svg ./gnumed-client.$CLIENTREV/client/bitmaps/
cp -R ../../client/bitmaps/gm_icon-serpent_and_gnu.xcf ./gnumed-client.$CLIENTREV/client/bitmaps/
cp -R ../../client/bitmaps/gm_icon-serpent_and_gnu.xpm ./gnumed-client.$CLIENTREV/client/bitmaps/

# business
mkdir -p ./gnumed-client.$CLIENTREV/client/business/
cp -R ../../client/business/*.py ./gnumed-client.$CLIENTREV/client/business/


# connectors
mkdir -p ./gnumed-client.$CLIENTREV/client/connectors/
cp -R ../../client/connectors/gm_ctl_client.* ./gnumed-client.$CLIENTREV/client/connectors/


# doc
mkdir -p ./gnumed-client.$CLIENTREV/client/doc/
cp -R ../../client/gm-from-vcs.conf ./gnumed-client.$CLIENTREV/client/doc/gnumed.conf.example
cp -R ../../client/doc/hook_script_example.py ./gnumed-client.$CLIENTREV/client/doc/hook_script_example.py
cp -R ../../client/doc/data-packs.conf.example ./gnumed-client.$CLIENTREV/client/doc/
cp -R ../../client/doc/man-pages/gnumed.1 ./gnumed-client.$CLIENTREV/client/doc/gnumed.1
cp -R ../../client/doc/man-pages/gm-print_doc.1 ./gnumed-client.$CLIENTREV/client/doc/gm-print_doc.1
cp -R ../../client/doc/man-pages/gm_ctl_client.1 ./gnumed-client.$CLIENTREV/client/doc/gm_ctl_client.1
cp -R ../../client/doc/man-pages/gm-install_arriba.8 ./gnumed-client.$CLIENTREV/client/doc/gm-install_arriba.8
cp -R ../../client/doc/man-pages/gm-remove_person.1 ./gnumed-client.$CLIENTREV/server/doc/


# etc
mkdir -p ./gnumed-client.$CLIENTREV/client/etc/gnumed/
cp -R ../../client/gm-from-vcs.conf ./gnumed-client.$CLIENTREV/client/etc/gnumed/gnumed-client.conf.example
cp -R ../../client/etc/gnumed/mime_type2file_extension.conf.example ./gnumed-client.$CLIENTREV/client/etc/gnumed/
cp -R ../../client/etc/gnumed/egk+kvk-demon.conf.example ./gnumed-client.$CLIENTREV/client/etc/gnumed/


# exporters
mkdir -p ./gnumed-client.$CLIENTREV/client/exporters/
cp -R ../../client/exporters/__init__.py ./gnumed-client.$CLIENTREV/client/exporters
cp -R ../../client/exporters/gmPatientExporter.py ./gnumed-client.$CLIENTREV/client/exporters


# locale
mkdir -p ./gnumed-client.$CLIENTREV/client/po/
cp -R ../../client/po/ca.po ./gnumed-client.$CLIENTREV/client/po
cp -R ../../client/po/de.po ./gnumed-client.$CLIENTREV/client/po
cp -R ../../client/po/el.po ./gnumed-client.$CLIENTREV/client/po
cp -R ../../client/po/es.po ./gnumed-client.$CLIENTREV/client/po
cp -R ../../client/po/fr.po ./gnumed-client.$CLIENTREV/client/po
cp -R ../../client/po/it.po ./gnumed-client.$CLIENTREV/client/po
cp -R ../../client/po/nb.po ./gnumed-client.$CLIENTREV/client/po
cp -R ../../client/po/nl.po ./gnumed-client.$CLIENTREV/client/po
cp -R ../../client/po/pl.po ./gnumed-client.$CLIENTREV/client/po
cp -R ../../client/po/pt.po ./gnumed-client.$CLIENTREV/client/po
cp -R ../../client/po/pt_BR.po ./gnumed-client.$CLIENTREV/client/po
cp -R ../../client/po/ru.po ./gnumed-client.$CLIENTREV/client/po

cd ../../client/po/
./create-gnumed_mo.sh ca
./create-gnumed_mo.sh de
./create-gnumed_mo.sh el
./create-gnumed_mo.sh es
./create-gnumed_mo.sh fr
./create-gnumed_mo.sh it
./create-gnumed_mo.sh nb
./create-gnumed_mo.sh nl
./create-gnumed_mo.sh pl
./create-gnumed_mo.sh pt
./create-gnumed_mo.sh pt_BR
./create-gnumed_mo.sh ru
cd -

cp -R ../../client/po/de-gnumed.mo ./gnumed-client.$CLIENTREV/client/po
cp -R ../../client/po/el-gnumed.mo ./gnumed-client.$CLIENTREV/client/po
cp -R ../../client/po/es-gnumed.mo ./gnumed-client.$CLIENTREV/client/po
cp -R ../../client/po/fr-gnumed.mo ./gnumed-client.$CLIENTREV/client/po
cp -R ../../client/po/it-gnumed.mo ./gnumed-client.$CLIENTREV/client/po
cp -R ../../client/po/nb-gnumed.mo ./gnumed-client.$CLIENTREV/client/po
cp -R ../../client/po/nl-gnumed.mo ./gnumed-client.$CLIENTREV/client/po
cp -R ../../client/po/pl-gnumed.mo ./gnumed-client.$CLIENTREV/client/po
cp -R ../../client/po/pt-gnumed.mo ./gnumed-client.$CLIENTREV/client/po
cp -R ../../client/po/pt_BR-gnumed.mo ./gnumed-client.$CLIENTREV/client/po
cp -R ../../client/po/ru-gnumed.mo ./gnumed-client.$CLIENTREV/client/po


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


# current User Manual
echo "picking up GNUmed User Manual from the web"
mkdir -p ./gnumed-client.$CLIENTREV/client/doc/user-manual/
cd ./gnumed-client.$CLIENTREV/client/doc/user-manual/
#wget -v -O ./GNUmed-User-Manual.zip http://wiki.gnumed.de/pub/publish/Gnumed.zip
#unzip GNUmed-User-Manual.zip
wget -v -O ./GNUmed-User-Manual.tgz http://wiki.gnumed.de/pub/publish/tgz.tgz
tar -xzf GNUmed-User-Manual.tgz
rm -vf Release-02.html
ln -s GnumedManual.html Gnumed/index.html
rm -vf GNUmed-User-Manual.tgz
cd -


# current API documentation
echo "downloading the API documentation"
mkdir -p ./gnumed-client.$CLIENTREV/client/doc/api/
cd ./gnumed-client.$CLIENTREV/client/doc/api/
wget -v -r -k -np -nd http://publicdb.gnumed.de/~ncq/gnumed/api/
cd -


# current schema documentation
echo "downloading SQL schema documentation"
mkdir -p ./gnumed-client.$CLIENTREV/client/doc/schema/
cd ./gnumed-client.$CLIENTREV/client/doc/schema/
wget -v -r -k -np -nd http://publicdb.gnumed.de/~ncq/gnumed/schema/gnumed_v17/gnumed-schema.html
wget -v -r -k -np -nd http://publicdb.gnumed.de/~ncq/gnumed/schema/gnumed_v17/gnumed-schema-no_audit.dot
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
cp -R ../../server/gm-fingerprint_db.py ./gnumed-client.$CLIENTREV/server/
cp -R ../../server/gm-dump_schema.sh ./gnumed-client.$CLIENTREV/server/

cp -R ../../server/gm-pg_upgradecluster-helper ./gnumed-client.$CLIENTREV/server/

cp -R ../../server/gm-backup_database.sh ./gnumed-client.$CLIENTREV/server/
cp -R ../../server/gm-restore_database.sh ./gnumed-client.$CLIENTREV/server/

cp -R ../../server/gm-backup_data.sh ./gnumed-client.$CLIENTREV/server/
cp -R ../../server/gm-restore_data.sh ./gnumed-client.$CLIENTREV/server/

cp -R ../../server/gm-zip+sign_backups.sh ./gnumed-client.$CLIENTREV/server/
cp -R ../../server/gm-move_backups_offsite.sh ./gnumed-client.$CLIENTREV/server/

cp -R ../../external-tools/gm-remove_person.sh ./gnumed-client.$CLIENTREV/server/

cp -R ../../server/gm-set_gm-dbo_password ./gnumed-client.$CLIENTREV/server/

cp -R ../../client/__init__.py ./gnumed-client.$CLIENTREV/server/


# pycommon/
mkdir -p ./gnumed-client.$CLIENTREV/server/pycommon
cp -R ../../client/pycommon/*.py ./gnumed-client.$CLIENTREV/server/pycommon/


# bootstrap/
mkdir -p ./gnumed-client.$CLIENTREV/server/bootstrap
cp -R ../../server/bootstrap/* ./gnumed-client.$CLIENTREV/server/bootstrap/


# doc
mkdir -p ./gnumed-client.$CLIENTREV/server/doc/schema
cp -R ../../server/bootstrap/README ./gnumed-client.$CLIENTREV/server/doc/
cp -R ../../client/doc/man-pages/gm-bootstrap_server.8 ./gnumed-client.$CLIENTREV/server/doc/
cp -R ../../client/doc/man-pages/gm-upgrade_server.8 ./gnumed-client.$CLIENTREV/server/doc/
cp -R ../../client/doc/man-pages/gm-fixup_server.8 ./gnumed-client.$CLIENTREV/server/doc/
cp -R ../../client/doc/man-pages/gm-backup_data.8 ./gnumed-client.$CLIENTREV/server/doc/
cp -R ../../client/doc/man-pages/gm-backup_database.8 ./gnumed-client.$CLIENTREV/server/doc/
cp -R ../../client/doc/man-pages/gm-zip+sign_backups.8 ./gnumed-client.$CLIENTREV/server/doc/
cp -R ../../client/doc/man-pages/gm-move_backups_offsite.8 ./gnumed-client.$CLIENTREV/server/doc/
cp -R ../../client/doc/man-pages/gm-restore_data.8 ./gnumed-client.$CLIENTREV/server/doc/
cp -R ../../client/doc/man-pages/gm-restore_database.8 ./gnumed-client.$CLIENTREV/server/doc/
cp -R ../../client/doc/man-pages/gm-dump_schema.8 ./gnumed-client.$CLIENTREV/server/doc/
cp -R ../../client/doc/man-pages/gm-adjust_db_settings.8 ./gnumed-client.$CLIENTREV/server/doc/
cp -R ../../client/doc/man-pages/gm-remove_person.1 ./gnumed-client.$CLIENTREV/server/doc/
cp -R ../../client/doc/man-pages/gm-set_gm-dbo_password.8 ./gnumed-client.$CLIENTREV/server/doc/
cp -R ../../client/doc/man-pages/gm-fingerprint_db.8 ./gnumed-client.$CLIENTREV/server/doc/
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
cp ../../server/sql/v2-v3/gm_db-gnumed_v*-fingerprint.txt ./gnumed-client.$CLIENTREV/server/sql/v2-v3
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v2-v3/dynamic
cp -R ../../server/sql/v2-v3/dynamic/*.sql ./gnumed-client.$CLIENTREV/server/sql/v2-v3/dynamic
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v2-v3/static
cp -R ../../server/sql/v2-v3/static/*.sql ./gnumed-client.$CLIENTREV/server/sql/v2-v3/static
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v2-v3/superuser
cp -R ../../server/sql/v2-v3/superuser/*.sql ./gnumed-client.$CLIENTREV/server/sql/v2-v3/superuser

mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v3-v4
cp ../../server/sql/v3-v4/gm_db-gnumed_v*-fingerprint.txt ./gnumed-client.$CLIENTREV/server/sql/v3-v4
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v3-v4/dynamic
cp -R ../../server/sql/v3-v4/dynamic/*.sql ./gnumed-client.$CLIENTREV/server/sql/v3-v4/dynamic
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v3-v4/static
cp -R ../../server/sql/v3-v4/static/*.sql ./gnumed-client.$CLIENTREV/server/sql/v3-v4/static
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v3-v4/superuser
cp -R ../../server/sql/v3-v4/superuser/*.sql ./gnumed-client.$CLIENTREV/server/sql/v3-v4/superuser

mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v4-v5
cp ../../server/sql/v4-v5/gm_db-gnumed_v*-fingerprint.txt ./gnumed-client.$CLIENTREV/server/sql/v4-v5
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v4-v5/dynamic
cp -R ../../server/sql/v4-v5/dynamic/*.sql ./gnumed-client.$CLIENTREV/server/sql/v4-v5/dynamic
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v4-v5/static
cp -R ../../server/sql/v4-v5/static/*.sql ./gnumed-client.$CLIENTREV/server/sql/v4-v5/static
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v4-v5/superuser
cp -R ../../server/sql/v4-v5/superuser/*.sql ./gnumed-client.$CLIENTREV/server/sql/v4-v5/superuser

mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v5-v6
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v5-v6/dynamic
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v5-v6/static

cp ../../server/sql/v5-v6/gm_db-gnumed_v*-fingerprint.txt ./gnumed-client.$CLIENTREV/server/sql/v5-v6
cp -R ../../server/sql/v5-v6/dynamic/*.sql ./gnumed-client.$CLIENTREV/server/sql/v5-v6/dynamic
cp -R ../../server/sql/v5-v6/static/*.sql ./gnumed-client.$CLIENTREV/server/sql/v5-v6/static


mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v6-v7
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v6-v7/dynamic
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v6-v7/static
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v6-v7/data
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v6-v7/python

cp ../../server/sql/v6-v7/gm_db-gnumed_v*-fingerprint.txt ./gnumed-client.$CLIENTREV/server/sql/v6-v7
cp -R ../../server/sql/v6-v7/dynamic/*.sql ./gnumed-client.$CLIENTREV/server/sql/v6-v7/dynamic
cp -R ../../server/sql/v6-v7/static/*.sql ./gnumed-client.$CLIENTREV/server/sql/v6-v7/static
cp -R ../../server/sql/v6-v7/data/* ./gnumed-client.$CLIENTREV/server/sql/v6-v7/data
cp -R ../../server/sql/v6-v7/python/*.py ./gnumed-client.$CLIENTREV/server/sql/v6-v7/python


mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v7-v8
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v7-v8/dynamic
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v7-v8/static

cp ../../server/sql/v7-v8/gm_db-gnumed_v*-fingerprint.txt ./gnumed-client.$CLIENTREV/server/sql/v7-v8
cp -R ../../server/sql/v7-v8/dynamic/*.sql ./gnumed-client.$CLIENTREV/server/sql/v7-v8/dynamic
cp -R ../../server/sql/v7-v8/static/*.sql ./gnumed-client.$CLIENTREV/server/sql/v7-v8/static


mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v8-v9
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v8-v9/dynamic
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v8-v9/static

cp ../../server/sql/v8-v9/gm_db-gnumed_v*-fingerprint.txt ./gnumed-client.$CLIENTREV/server/sql/v8-v9
cp -R ../../server/sql/v8-v9/dynamic/*.sql ./gnumed-client.$CLIENTREV/server/sql/v8-v9/dynamic
cp -R ../../server/sql/v8-v9/static/*.sql ./gnumed-client.$CLIENTREV/server/sql/v8-v9/static


mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v9-v10
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v9-v10/dynamic
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v9-v10/static
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v9-v10/superuser
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v9-v10/fixups

cp ../../server/sql/v9-v10/gm_db-gnumed_v*-fingerprint.txt ./gnumed-client.$CLIENTREV/server/sql/v9-v10
cp -R ../../server/sql/v9-v10/dynamic/*.sql ./gnumed-client.$CLIENTREV/server/sql/v9-v10/dynamic
cp -R ../../server/sql/v9-v10/static/*.sql ./gnumed-client.$CLIENTREV/server/sql/v9-v10/static
cp -R ../../server/sql/v9-v10/superuser/*.sql ./gnumed-client.$CLIENTREV/server/sql/v9-v10/superuser
cp -R ../../server/sql/v9-v10/fixups/*.sql ./gnumed-client.$CLIENTREV/server/sql/v9-v10/fixups


mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v10-v11
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v10-v11/dynamic
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v10-v11/static
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v10-v11/superuser
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v10-v11/fixups

cp ../../server/sql/v10-v11/gm_db-gnumed_v*-fingerprint.txt ./gnumed-client.$CLIENTREV/server/sql/v10-v11
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

cp ../../server/sql/v11-v12/gm_db-gnumed_v*-fingerprint.txt ./gnumed-client.$CLIENTREV/server/sql/v11-v12
cp -R ../../server/sql/v11-v12/dynamic/*.sql ./gnumed-client.$CLIENTREV/server/sql/v11-v12/dynamic
cp -R ../../server/sql/v11-v12/static/*.sql ./gnumed-client.$CLIENTREV/server/sql/v11-v12/static
cp -R ../../server/sql/v11-v12/superuser/*.sql ./gnumed-client.$CLIENTREV/server/sql/v11-v12/superuser
cp -R ../../server/sql/v11-v12/data/* ./gnumed-client.$CLIENTREV/server/sql/v11-v12/data
cp -R ../../server/sql/v11-v12/python/*.py ./gnumed-client.$CLIENTREV/server/sql/v11-v12/python


mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v12-v13
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v12-v13/dynamic
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v12-v13/static
#mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v12-v13/superuser
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v12-v13/data
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v12-v13/python
#mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v12-v13/fixups

cp ../../server/sql/v12-v13/gm_db-gnumed_v*-fingerprint.txt ./gnumed-client.$CLIENTREV/server/sql/v12-v13
cp -R ../../server/sql/v12-v13/dynamic/*.sql ./gnumed-client.$CLIENTREV/server/sql/v12-v13/dynamic
cp -R ../../server/sql/v12-v13/static/*.sql ./gnumed-client.$CLIENTREV/server/sql/v12-v13/static
#cp -R ../../server/sql/v12-v13/superuser/*.sql ./gnumed-client.$CLIENTREV/server/sql/v12-v13/superuser
cp -R ../../server/sql/v12-v13/data/* ./gnumed-client.$CLIENTREV/server/sql/v12-v13/data
cp -R ../../server/sql/v12-v13/python/*.py ./gnumed-client.$CLIENTREV/server/sql/v12-v13/python
#cp -R ../../server/sql/v12-v13/fixups/*.sql ./gnumed-client.$CLIENTREV/server/sql/v12-v13/fixups


mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v13-v14
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v13-v14/dynamic
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v13-v14/static
#mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v13-v14/superuser
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v13-v14/data
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v13-v14/python
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v13-v14/fixups

cp ../../server/sql/v13-v14/gm_db-gnumed_v*-fingerprint.txt ./gnumed-client.$CLIENTREV/server/sql/v13-v14
cp -R ../../server/sql/v13-v14/dynamic/*.sql ./gnumed-client.$CLIENTREV/server/sql/v13-v14/dynamic
cp -R ../../server/sql/v13-v14/static/*.sql ./gnumed-client.$CLIENTREV/server/sql/v13-v14/static
#cp -R ../../server/sql/v13-v14/superuser/*.sql ./gnumed-client.$CLIENTREV/server/sql/v13-v14/superuser
cp -R ../../server/sql/v13-v14/data/* ./gnumed-client.$CLIENTREV/server/sql/v13-v14/data
cp -R ../../server/sql/v13-v14/python/*.py ./gnumed-client.$CLIENTREV/server/sql/v13-v14/python
cp -R ../../server/sql/v13-v14/fixups/*.sql ./gnumed-client.$CLIENTREV/server/sql/v13-v14/fixups


mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v14-v15
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v14-v15/dynamic
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v14-v15/static
#mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v14-v15/superuser
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v14-v15/data
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v14-v15/python
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v14-v15/fixups

cp ../../server/sql/v14-v15/gm_db-gnumed_v*-fingerprint.txt ./gnumed-client.$CLIENTREV/server/sql/v14-v15
cp -R ../../server/sql/v14-v15/dynamic/*.sql ./gnumed-client.$CLIENTREV/server/sql/v14-v15/dynamic
cp -R ../../server/sql/v14-v15/static/*.sql ./gnumed-client.$CLIENTREV/server/sql/v14-v15/static
#cp -R ../../server/sql/v14-v15/superuser/*.sql ./gnumed-client.$CLIENTREV/server/sql/v14-v15/superuser
cp -R ../../server/sql/v14-v15/data/* ./gnumed-client.$CLIENTREV/server/sql/v14-v15/data
cp -R ../../server/sql/v14-v15/python/*.py ./gnumed-client.$CLIENTREV/server/sql/v14-v15/python
cp -R ../../server/sql/v14-v15/fixups/*.sql ./gnumed-client.$CLIENTREV/server/sql/v14-v15/fixups


mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v15-v16
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v15-v16/dynamic
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v15-v16/static
#mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v15-v16/superuser
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v15-v16/data
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v15-v16/python
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v15-v16/fixups

cp ../../server/sql/v15-v16/gm_db-gnumed_v*-fingerprint.txt ./gnumed-client.$CLIENTREV/server/sql/v15-v16
cp -R ../../server/sql/v15-v16/dynamic/*.sql ./gnumed-client.$CLIENTREV/server/sql/v15-v16/dynamic
cp -R ../../server/sql/v15-v16/static/*.sql ./gnumed-client.$CLIENTREV/server/sql/v15-v16/static
#cp -R ../../server/sql/v15-v16/superuser/*.sql ./gnumed-client.$CLIENTREV/server/sql/v15-v16/superuser
cp -R ../../server/sql/v15-v16/data/* ./gnumed-client.$CLIENTREV/server/sql/v15-v16/data
cp -R ../../server/sql/v15-v16/python/*.py ./gnumed-client.$CLIENTREV/server/sql/v15-v16/python
cp -R ../../server/sql/v15-v16/fixups/*.sql ./gnumed-client.$CLIENTREV/server/sql/v15-v16/fixups


mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v16-v17
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v16-v17/dynamic
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v16-v17/static
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v16-v17/data
mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v16-v17/python
#mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v16-v17/fixups
#mkdir -p ./gnumed-client.$CLIENTREV/server/sql/v16-v17/superuser

cp ../../server/sql/v16-v17/gm_db-gnumed_v*-fingerprint.txt ./gnumed-client.$CLIENTREV/server/sql/v16-v17
cp -R ../../server/sql/v16-v17/dynamic/*.sql ./gnumed-client.$CLIENTREV/server/sql/v16-v17/dynamic
cp -R ../../server/sql/v16-v17/static/*.sql ./gnumed-client.$CLIENTREV/server/sql/v16-v17/static
cp -R ../../server/sql/v16-v17/data/* ./gnumed-client.$CLIENTREV/server/sql/v16-v17/data
cp -R ../../server/sql/v16-v17/python/*.py ./gnumed-client.$CLIENTREV/server/sql/v16-v17/python
#cp -R ../../server/sql/v16-v17/fixups/*.sql ./gnumed-client.$CLIENTREV/server/sql/v16-v17/fixups
#cp -R ../../server/sql/v16-v17/superuser/*.sql ./gnumed-client.$CLIENTREV/server/sql/v16-v17/superuser

#----------------------------------
# weed out unnecessary stuff
for fname in $FILES_REMOVE ; do
	rm -f $fname
done ;


echo "cleaning out debris"
find ./ -name '*.pyc' -exec rm -v '{}' ';'
find ./ -name '*.py~' -exec rm -v '{}' ';'
find ./ -name 'wxg*.wxg~' -exec rm -v '{}' ';'
find ./ -name '*.log' -exec rm -v '{}' ';'
find ./gnumed-client.$CLIENTREV/ -name 'wxg' -type d -exec rm -v -r '{}' ';'


# now make tarballs
# - client
cd gnumed-client.$CLIENTREV
ln -sT client Gnumed
cd ..
tar -czf $CLIENTARCH ./gnumed-client.$CLIENTREV/client/ ./gnumed-client.$CLIENTREV/external-tools/ ./gnumed-client.$CLIENTREV/Gnumed

md5sum $CLIENTARCH > $CLIENTARCH.md5
echo "" >> $CLIENTARCH.md5
echo "Verify this MD5 sum by running:" >> $CLIENTARCH.md5
echo " md5sum $CLIENTARCH" >> $CLIENTARCH.md5

sha512sum $CLIENTARCH > $CLIENTARCH.sha512
echo "" >> $CLIENTARCH.sha512
echo "Verify this SHA512 sum by running:" >> $CLIENTARCH.sha512
echo " sha512sum $CLIENTARCH" >> $CLIENTARCH.sha512

# - server
mv gnumed-client.$CLIENTREV gnumed-server.$SRVREV
cd gnumed-server.$SRVREV
rm Gnumed
ln -sT server Gnumed
cd ..
tar -czf $SRVARCH ./gnumed-server.$SRVREV/server/ ./gnumed-server.$SRVREV/Gnumed

md5sum $SRVARCH > $SRVARCH.md5
echo "" >> $SRVARCH.md5
echo "Verify this MD5 sum by running:" >> $SRVARCH.md5
echo " md5sum $SRVARCH" >> $SRVARCH.md5

sha512sum $SRVARCH > $SRVARCH.sha512
echo "" >> $SRVARCH.sha512
echo "Verify this SHA512 sum by running:" >> $SRVARCH.sha512
echo " sha512sum $SRVARCH" >> $SRVARCH.sha512

# cleanup
rm -R ./gnumed-server.$SRVREV/

echo "include schema docs"

# upload
scp $CLIENTARCH $CLIENTARCH.md5 $CLIENTARCH.sha512 $SRVARCH $SRVARCH.md5 $SRVARCH.sha512 www.gnumed.de:

# post announcement ?
