-- ===============================================
-- stub for loading data into AMIS tables

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/Attic/amis-data.sql,v $
-- author: Horst Herb, Hilmar Berger, Karsten Hilbert
-- version: $Revision: 1.2 $
-- license: GPL

-- get the correct AMIS_PATH and process the template file 
\set AMIS_PATH `./amis_get_dir.sh`

-- run the script created from template
\i 'amis-import_data.sql'

-- set the config information in the backend
\echo `env PYTHONPATH=../../../bootstrap/modules ../../../bootstrap/modules/tools/transferDBset.py -i ./amis-config.set`

-- ===============================================
-- $Log: amis-data.sql,v $
-- Revision 1.2  2003-10-26 22:49:54  hinnef
-- - added config parameter sets
--
-- Revision 1.1  2003/10/26 18:10:06  ncq
-- - separate schema and data better
--
