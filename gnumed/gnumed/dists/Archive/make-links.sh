#!/bin/sh
#----------------------------------
# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/dists/Archive/Attic/make-links.sh,v $
# $Revision: 1.14 $
# GPL
# Karsten.Hilbert@gmx.net
#----------------------------------
echo "setting up links for GnuMed/Archive tgz creation"

#----------------------------------
echo "_____________"
echo "=> modules <="
echo "============="

mkdir modules
ln -vs ../../../client/python-common/gmLog.py modules/gmLog.py
ln -vs ../../../client/python-common/gmI18N.py modules/gmI18N.py
ln -vs ../../../client/python-common/gmCfg.py modules/gmCfg.py
ln -vs ../../../client/python-common/gmCLI.py modules/gmCLI.py
ln -vs ../../../client/python-common/gmPG.py modules/gmPG.py
ln -vs ../../../client/python-common/gmBackendListener.py modules/gmBackendListener.py
ln -vs ../../../client/python-common/gmDispatcher.py modules/gmDispatcher.py
ln -vs ../../../client/python-common/gmSignals.py modules/gmSignals.py
ln -vs ../../../client/python-common/gmLoginInfo.py modules/gmLoginInfo.py
ln -vs ../../../client/python-common/gmExceptions.py modules/gmExceptions.py
ln -vs ../../../client/python-common/gmMimeLib.py modules/gmMimeLib.py
ln -vs ../../../client/python-common/gmMimeMagic.py modules/gmMimeMagic.py
ln -vs ../../../client/python-common/gmBorg.py modules/gmBorg.py

ln -vs ../../../client/business/gmTmpPatient.py modules/gmTmpPatient.py
ln -vs ../../../client/business/gmMedDoc.py modules/gmMedDoc.py
ln -vs ../../../client/business/gmXdtObjects.py modules/gmXdtObjects.py
ln -vs ../../../client/business/gmXdtMappings.py modules/gmXdtMappings.py
ln -vs ../../../client/business/gmXmlDocDesc.py modules/gmXmlDocDesc.py

ln -vs ../../../test-area/blobs_hilbert/modules/docPatient.py modules/docPatient.py
ln -vs ../../../test-area/blobs_hilbert/modules/docDocument.py modules/docDocument.py
ln -vs ../../../test-area/blobs_hilbert/modules/docDatabase.py modules/docDatabase.py

#----------------------------------
echo "____________"
echo "=> client <="
echo "============"

mkdir client
ln -vs ../modules client/modules

# viewer
ln -vs ../../../client/wxpython/gui/gmShowMedDocs.py client/gmShowMedDocs.py
ln -vs ../../../Archive/viewer/run-viewer.sh client/run-viewer.sh
ln -vs ../../../Archive/viewer/run-viewer.bat client/run-viewer.bat

# docs
ln -vs ../../../Archive/client/sample.conf client/sample.conf
ln -vs ../../../Archive/client/README client/README
ln -vs ../../../Archive/client/README-GnuMed-Archiv-de.txt client/README-GnuMed-Archiv-de.txt
ln -vs ../../../Archive/client/README-GnuMed-Archiv-en.txt client/README-GnuMed-Archiv-en.txt

# locale
mkdir -p client/locale/de_DE@euro/LC_MESSAGES
ln -vs ../../../../../../client/locale/de-gnumed.mo client/locale/de_DE@euro/LC_MESSAGES/gnumed.mo

# installation/bootstrapping
ln -vs ../../../Archive/client/install.sh client/install.sh

#ln -vs ../../scan/gmScanMedDocs.py client/gmScanMedDocs.py
#ln -vs ~/.gnumed/gnumed-archive.conf client/gnumed-archive.conf
#ln -vs ../../import/import-med_docs.py client/import-med_docs.py
#ln -vs ../../index/index-med_docs.py client/index-med_docs.py
#ln -vs ../../import/run-importer.bat client/run-importer.bat
#ln -vs ../../import/run-importer.sh client/run-importer.sh
#ln -vs ../../import/remove-imported_dirs.sh client/remove-imported_dirs.sh
#ln -vs ../../index/run-indexer.bat client/run-indexer.bat
#ln -vs ../../index/run-indexer.sh client/run-indexer.sh
#ln -vs ../../scan/run-scanner.bat client/run-scanner.bat
#ln -vs ../../scan/run-scanner.sh client/run-scanner.sh

#mkdir client/doc
#ln -vs ../../../docs/README-GnuMed-Archiv-de.txt client/doc/README-GnuMed-Archiv-de.txt
#ln -vs ../../../docs/TODO client/doc/TODO

#----------------------------------
echo "____________"
echo "=> server <="
echo "============"

mkdir server
ln -vs ../modules server/modules
ln -vs ../../../server/sql server/sql

# importer
ln -vs ../../../Archive/import/import-med_docs.py server/import-med_docs.py
ln -vs ../../../Archive/import/remove-imported_dirs.sh server/remove-imported_dirs.sh
ln -vs ../../../Archive/import/run-importer.sh server/run-importer.sh
ln -vs ../../../Archive/import/run-importer.bat server/run-importer.bat

# installation/bootstrapping
ln -vs ../../../server/bootstrap/bootstrap-gm_db_system.py server/bootstrap-gm_db_system.py
ln -vs ../../../server/bootstrap/bootstrap-archive.conf server/bootstrap-archive.conf
ln -vs ../../../Archive/server/gmArchiveAccounts.sql server/gmArchiveAccounts.sql
ln -vs ../../../Archive/server/install.sh server/install.sh
ln -vs ../../../Archive/server/dropBlobs.sql server/dropBlobs.sql

# docs
ln -vs ../../../Archive/server/README server/README
