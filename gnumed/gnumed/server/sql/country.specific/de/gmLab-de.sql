-- lab related tables specific to Germany (billing)

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/Attic/gmLab-de.sql,v $
-- $Revision: 1.2 $
-- =============================================

-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
CREATE TABLE lab_test_GNR (
	test_id integer references lab_test,
	EBM character(6) references ebm.gnr,
	GOA_88 character(6) references goae_88.gnr,
	GOA_96 character(6) references goae_96.gnr,
	UVT_GOA character(6) references bg_goae.gnr
) INHERITS (audit_identity);

COMMENT ON TABLE lab_test_GNR is "specific for Germany, GNR = GebührenordnungsNummeR = billing item, build index before lab import and drop afterwards, check against this table when importing, build table during import";
COMMENT ON COLUMN lab_test_GNR.test_id IS "link to test in our practice";
COMMENT ON COLUMN lab_test_GNR.EBM is "GNR according to EBM (Einheitlicher BewertungsMaßstab) for Kassenpatienten (gov't insured patients)";
COMMENT ON COLUMN lab_test_GNR.GOA_88 is "GNR according to GOAe '88 (GebuehrenOrdnung für Aerzte) for Privatpatienten (privately insured patients)";
COMMENT ON COLUMN lab_test_GNR.GOA_96 is "GNR according to GOAe '96 (GebuehrenOrdnung für Aerzte) for Privatpatienten (privately insured patients)";
COMMENT ON COLUMN lab_test_GNR.BG_GOA is "GNR according to GOAe (GebuehrenOrdnung für Aerzte) for Berufsgenossenschaften (sector specific job related health insurance)";

-- =============================================
-- do simple revision tracking
\i gmSchemaRevision.sql
INSERT INTO schema_revision (filename, version) VALUES('$RCSfile: gmLab-de.sql,v $', '$Revision: 1.2 $')

-- =============================================
-- $Log: gmLab-de.sql,v $
-- Revision 1.2  2002-11-16 01:09:57  ncq
-- - revision tracking
--
