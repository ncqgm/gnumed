-- lab related tables specific to Germany (billing)

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/gmClinical.de.sql,v $
-- $Revision: 1.1 $
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
CREATE TABLE lab_test_GNR (
	id serial primary key,
	id_test integer not null references test_type(id)
--	EBM character(6) references ebm(gnr),
--	GOA_88 character(6) references goae_88.gnr,
--	GOA_96 character(6) references goae_96.gnr
--	UVT_GOA character(6) references bg_goae(gnr)
) inherits (audit_mark, audit_fields);

COMMENT ON TABLE lab_test_GNR is
	'specific for Germany, GNR = GebührenordnungsNummeR = billing
	 item, build index before lab import and drop afterwards, check
	 against this table when importing, build table during import';
COMMENT ON COLUMN lab_test_GNR.id_test IS
	'link to test in our practice';
/*
COMMENT ON COLUMN lab_test_GNR.EBM is
	'GNR according to EBM (Einheitlicher BewertungsMaßstab)
	 for Kassenpatienten (gov''t insured patients)';
COMMENT ON COLUMN lab_test_GNR.GOA_88 is
	'GNR according to GOAe 88 (GebuehrenOrdnung für Aerzte)
	 for Privatpatienten (privately insured patients)';
COMMENT ON COLUMN lab_test_GNR.GOA_96 is
	'GNR according to GOAe 96 (GebuehrenOrdnung für Aerzte)
	 for Privatpatienten (privately insured patients)';
COMMENT ON COLUMN lab_test_GNR.BG_GOA is
	'GNR according to GOAe (GebuehrenOrdnung für Aerzte) for
	 Berufsgenossenschaften (sector specific job related
	 health insurance)';
*/

create table log_lab_test_GNR (
	id integer not null,
	id_test integer not null
--	EBM character(6) references ebm(gnr),
--	GOA_88 character(6) references goae_88.gnr,
--	GOA_96 character(6) references goae_96.gnr
--	UVT_GOA character(6) references bg_goae(gnr)
) inherits (audit_trail);

-- =============================================
-- do simple revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmClinical.de.sql,v $', '$Revision: 1.1 $')

-- =============================================
-- $Log: gmClinical.de.sql,v $
-- Revision 1.1  2003-08-05 08:16:00  ncq
-- - cleanup/renaming
--
-- Revision 1.5  2003/07/27 22:02:18  ncq
-- - test_id -> id_test
--
-- Revision 1.4  2003/05/12 12:43:40  ncq
-- - gmI18N, gmServices and gmSchemaRevision are imported globally at the
--   database level now, don't include them in individual schema file anymore
--
-- Revision 1.3  2003/01/05 13:05:53  ncq
-- - schema_revision -> gm_schema_revision
--
-- Revision 1.2  2002/11/16 01:09:57  ncq
-- - revision tracking
--
