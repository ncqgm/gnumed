-- ===============================================
-- stub for loading data into AMIS tables

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/Attic/amis-data.sql,v $
-- author: Horst Herb, Hilmar Berger, Karsten Hilbert
-- version: $Revision: 1.1 $
-- license: GPL

-- get the correct AMIS_PATH and process the template file 
\set AMIS_PATH `./amis_get_dir.sh`

-- run the script created from template
\i 'amis-import_data.sql'

-- ===============================================
-- $Log: amis-data.sql,v $
-- Revision 1.1  2003-10-26 18:10:06  ncq
-- - separate schema and data better
--
