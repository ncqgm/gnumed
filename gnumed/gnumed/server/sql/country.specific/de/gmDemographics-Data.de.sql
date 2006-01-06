-- GnuMed
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/gmDemographics-Data.de.sql,v $
-- $Revision: 1.6 $

-- license: GPL
-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>

-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

set client_encoding to 'LATIN1';
-- =============================================
-- external ID types
insert into dem.enum_ext_id_types (name, issuer, context) values ('KV-Nummer', 'KV', 'c');
insert into dem.enum_ext_id_types (name, issuer, context) values ('Mitgliedsnummer', 'Krankenkasse', 'p');
insert into dem.enum_ext_id_types (name, issuer, context) values ('BLZ', 'Bank', 'o');

--insert into dem.enum_ext_id_types (name, issuer, context) values ('', '', '');
-- =============================================
-- do simple revision tracking
delete from gm_schema_revision where filename = '$RCSfile: gmDemographics-Data.de.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmDemographics-Data.de.sql,v $', '$Revision: 1.6 $');

-- =============================================
-- $Log: gmDemographics-Data.de.sql,v $
-- Revision 1.6  2006-01-06 10:12:02  ncq
-- - add missing grants
-- - add_table_for_audit() now in "audit" schema
-- - demographics now in "dem" schema
-- - add view v_inds4vaccine
-- - move staff_role from clinical into demographics
-- - put add_coded_term() into "clin" schema
-- - put German things into "de_de" schema
--
-- Revision 1.5  2005/09/19 16:38:52  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.4  2005/07/14 21:31:43  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.3  2005/03/31 20:10:16  ncq
-- - aggregate translations
--
-- Revision 1.2  2004/03/04 10:53:07  ncq
-- - add a bunch of external id types
--
-- Revision 1.1  2003/08/05 08:16:00  ncq
-- - cleanup/renaming
--
-- Revision 1.3  2003/06/11 14:03:44  ncq
-- - set encoding
--
-- Revision 1.2  2003/05/12 12:43:40  ncq
-- - gmI18N, gmServices and gmSchemaRevision are imported globally at the
--   database level now, don't include them in individual schema file anymore
--
-- Revision 1.1  2003/01/22 23:40:18  ncq
-- - first version
--
