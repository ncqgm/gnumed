-- project: GNUMed
-- database: (global)
-- purpose:  see comment below
-- author: hherb
-- copyright: Dr. Horst Herb, horst@hherb.com
-- license: GPL (details at http://gnu.org)
-- version: 0.4
-- changelog:
-- 08.03.2002:  (hherb) first useable version
--
-- gnumed.sql: this should be the first sql script to run
-- when you want to install a gnumed system.
-- Initially, It contains mainly administrativa, such as
-- the installation of theneccessary procedural languages.
-- You might need to adjust the library paths.
-- Ultimately, this script should generate a whole new gnumed
-- backend without anything further to do apart from running it


-- maybe the script should search automatically for the
-- correct library path? Or prompt the user?

-- create the neccessary procedural languages
-- you may have to modify the path to the shared library according to your postgresql installation
CREATE FUNCTION plpgsql_call_handler () RETURNS OPAQUE AS
    '/usr/lib/pgsql/plpgsql.so' LANGUAGE 'C';

CREATE TRUSTED PROCEDURAL LANGUAGE 'plpgsql'
    HANDLER plpgsql_call_handler
    LANCOMPILER 'PL/pgSQL';

CREATE FUNCTION plpython_call_handler () RETURNS OPAQUE AS
    '/usr/lib/pgsql/plpython.so' LANGUAGE 'C';

CREATE TRUSTED PROCEDURAL LANGUAGE 'plpython'
    HANDLER plpython_call_handler;

-- TODO:
-- create configuration database
-- connect to it
-- run gmconfiguration.sql
-- ask user if and how to split information into multiple databases
-- create geographic / demographic databases accordingly
-- connect to them
-- run respective scripts gmgis.sql and gmidentity.sql
-- connect to configuration database
-- update information about geographic / demographic database
-- ...
