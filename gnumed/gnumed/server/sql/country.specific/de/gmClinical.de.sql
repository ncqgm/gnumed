-- lab related tables specific to Germany (billing)

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/de/gmClinical.de.sql,v $
-- $Revision: 1.17 $
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

reset client_encoding;
-- =============================================
CREATE TABLE de_de.lab_test_GNR (
	id serial primary key,
	id_test integer
		not null
		references clin.test_type(pk)
) inherits (audit.audit_fields);

--	EBM character(6) references ebm(gnr),
--	GOA_88 character(6) references goae_88.gnr,
--	GOA_96 character(6) references goae_96.gnr
--	UVT_GOA character(6) references bg_goae(gnr)

select audit.add_table_for_audit('de_de', 'lab_test_gnr');

COMMENT ON TABLE de_de.lab_test_GNR is
	'specific for Germany, GNR = GebuehrenordnungsNummeR = billing
	 item, build index before lab import and drop afterwards, check
	 against this table when importing, build table during import';
COMMENT ON COLUMN de_de.lab_test_GNR.id_test IS
	'link to test in our practice';
--COMMENT ON COLUMN de_de.lab_test_GNR.EBM is
--	'GNR according to EBM (Einheitlicher BewertungsMassstab)
--	 for Kassenpatienten (gov''t insured patients)';
--COMMENT ON COLUMN de_de.lab_test_GNR.GOA_88 is
--	'GNR according to GOAe 88 (GebuehrenOrdnung fuer Aerzte)
--	 for Privatpatienten (privately insured patients)';
--COMMENT ON COLUMN de_de.lab_test_GNR.GOA_96 is
--	'GNR according to GOAe 96 (GebuehrenOrdnung fuer Aerzte)
--	 for Privatpatienten (privately insured patients)';
--COMMENT ON COLUMN de_de.lab_test_GNR.BG_GOA is
--	'GNR according to GOAe (GebuehrenOrdnung fuer Aerzte) for
--	 Berufsgenossenschaften (sector specific job related
--	 health insurance)';

-- =============================================
-- do simple revision tracking
delete from gm_schema_revision where filename='$RCSfile: gmClinical.de.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmClinical.de.sql,v $', '$Revision: 1.17 $');

-- =============================================
-- $Log: gmClinical.de.sql,v $
-- Revision 1.17  2006-01-06 10:12:02  ncq
-- - add missing grants
-- - add_table_for_audit() now in "audit" schema
-- - demographics now in "dem" schema
-- - add view v_inds4vaccine
-- - move staff_role from clinical into demographics
-- - put add_coded_term() into "clin" schema
-- - put German things into "de_de" schema
--
-- Revision 1.16  2006/01/05 16:04:37  ncq
-- - move auditing to its own schema "audit"
--
-- Revision 1.15  2005/11/25 15:07:28  ncq
-- - create schema "clin" and move all things clinical into it
--
-- Revision 1.14  2005/09/19 16:38:52  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.13  2005/07/14 21:31:43  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.12  2004/09/29 19:15:45  ncq
-- - id -> pk
--
-- Revision 1.11  2004/01/09 02:59:28  ncq
-- - reset client encoding
--
-- Revision 1.10  2003/12/29 16:01:54  uid66147
-- - umlauts breakage
--
-- Revision 1.9  2003/11/05 23:02:38  hinnef
-- rollback
--
-- Revision 1.8  2003/11/05 23:00:37  hinnef
-- moved AMIS installation scripts to bootstrap dir
--
-- Revision 1.7  2003/11/02 12:49:41  ncq
-- - fix psql.py lossage
--
-- Revision 1.6  2003/10/26 16:10:59  hinnef
-- rollback
--
-- Revision 1.5  2003/10/26 16:07:07  hinnef
-- initial AMIS-schema and data import
--
-- Revision 1.4  2003/10/19 13:52:20  ncq
-- - add missing ;
--
-- Revision 1.3  2003/10/01 15:45:20  ncq
-- - use add_table_for_audit() instead of inheriting from audit_mark
--
-- Revision 1.2  2003/08/17 00:28:25  ncq
-- - removed log_ table since now autocreated
--
-- Revision 1.1  2003/08/05 08:16:00  ncq
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
