#!/bin/sh

# $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/blobs_hilbert/dist/Attic/make-links.sh,v $
# $Revision: 1.1 $
# GPL
# Karsten.Hilbert@gmx.net

echo "setting up links for tgz creation"

echo "=> client"
mkdir client
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/test-area/blobs_hilbert/scan/gmScanMedDocs.py client/gmScanMedDocs.py
ln -vfs /home/ncq/.gnumed/gnumed-archive.conf client/gnumed-archive.conf
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/test-area/blobs_hilbert/import/import-med_docs.py client/import-med_docs.py
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/test-area/blobs_hilbert/index/index-med_docs.py client/index-med_docs.py
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/test-area/blobs_hilbert/import/run-importer.bat client/run-importer.bat
ln -vfs ../../import/run-importer.sh client/run-importer.sh
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/test-area/blobs_hilbert/index/run-indexer.bat client/run-indexer.bat
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/test-area/blobs_hilbert/index/run-indexer.sh client/run-indexer.sh
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/test-area/blobs_hilbert/scan/run-scanner.bat client/run-scanner.bat
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/test-area/blobs_hilbert/scan/run-scanner.sh client/run-scanner.sh
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/test-area/blobs_hilbert/viewer-tree/run-viewer.bat client/run-viewer.bat
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/test-area/blobs_hilbert/viewer-tree/run-viewer.sh client/run-viewer.sh
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/test-area/blobs_hilbert/viewer-tree/show-med_docs.py client/show-med_docs.py
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/test-area/blobs_hilbert/modules client/modules

mkdir client/doc
ln -vfs ../../../client/README client/doc/README
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/test-area/blobs_hilbert/docs/README-GnuMed-Archiv-de.txt client/doc/README-GnuMed-Archiv-de.txt
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/test-area/blobs_hilbert/docs/sample.conf client/doc/sample.conf
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/test-area/blobs_hilbert/docs/TODO client/doc/TODO

mkdir client/locale
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/test-area/blobs_hilbert/locale/de_DE@euro client/locale/de_DE@euro

echo "=> server"
mkdir server
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/test-area/blobs_hilbert/server/bootstrap-gm_db_system.conf server/bootstrap-gm_db_system.conf
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/server/utils/bootstrap-gm_db_system.py server/bootstrap-gm_db_system.py
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/server/sql/country.specific/de/german-doc_types.sql server/german-doc_types.sql
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/server/sql/gmBlobs.sql server/gmBlobs.sql
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/server/sql/gmconfiguration.sql server/gmconfiguration.sql
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/server/sql/gmgis.sql server/gmgis.sql
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/server/sql/gmidentity.sql server/gmidentity.sql
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/server/sql/gmSchemaRevision.sql server/gmSchemaRevision.sql
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/server/utils/gmUserSetup.py server/gmUserSetup.py
ln -vfs /home/ncq/.gnumed/gnumed-archive.conf server/gnumed-archive.conf
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/test-area/blobs_hilbert/import/import-med_docs.py server/import-med_docs.py
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/test-area/blobs_hilbert/server/install.sh server/install.sh
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/test-area/blobs_hilbert/modules server/modules
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/test-area/blobs_hilbert/server/README server/README
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/test-area/blobs_hilbert/import/run-importer.sh server/run-importer.sh
ln -vfs /home/ncq/Projekte/GNUmed/gnumed/gnumed/server/utils/setup-local_users.conf.sample server/setup-local_users.conf.sample
