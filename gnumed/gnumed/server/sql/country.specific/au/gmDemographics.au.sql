-- Project: GnuMed
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/au/gmDemographics.au.sql,v $
-- $Revision: 1.15 $
-- license: GPL
-- authors: Ian Haywood, Horst Herb, Karsten Hilbert, Richard Terry

-- demographics tables specific für Australia

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

reset client_encoding;
-- ===================================================================


-- ===================================================================

-- seeding for occupations list
-- this is highly nation-specific!

insert into dem.occupation (name) values ('doctor');
insert into dem.occupation (name) values ('general practitioner');
insert into dem.occupation (name) values ('hospital resident');
insert into dem.occupation (name) values ('hospital registrar');
insert into dem.occupation (name) values ('physician');
insert into dem.occupation (name) values ('cardiologist');
insert into dem.occupation (name) values ('gastroenterologist');
insert into dem.occupation (name) values ('respiratory physician');
insert into dem.occupation (name) values ('neurologist');
insert into dem.occupation (name) values ('dermatologist');
insert into dem.occupation (name) values ('rheumatologist');
insert into dem.occupation (name) values ('geneticist');
insert into dem.occupation (name) values ('pathologist');
insert into dem.occupation (name) values ('obstetrician/gynaecologist');
insert into dem.occupation (name) values ('paediatrician');
insert into dem.occupation (name) values ('psychiatrist');
insert into dem.occupation (name) values ('anaesthetist');
insert into dem.occupation (name) values ('radiologist');
insert into dem.occupation (name) values ('surgeon');
insert into dem.occupation (name) values ('general surgeon');
insert into dem.occupation (name) values ('plastic surgeon');
insert into dem.occupation (name) values ('orthopaedic surgeon');
insert into dem.occupation (name) values ('vascular surgeon');
insert into dem.occupation (name) values ('paediatric surgeon');
insert into dem.occupation (name) values ('neurosurgeon');
insert into dem.occupation (name) values ('cardio-thoracic surgeon');
insert into dem.occupation (name) values ('ENT surgeon');
insert into dem.occupation (name) values ('ophthalmologist');

insert into dem.occupation (name) values ('nurse');
insert into dem.occupation (name) values ('social worker');
insert into dem.occupation (name) values ('physiotherapist');
insert into dem.occupation (name) values ('speech pathologist');
insert into dem.occupation (name) values ('psychologist');
insert into dem.occupation (name) values ('occupational therapist');
insert into dem.occupation (name) values ('dietician');
insert into dem.occupation (name) values ('radiographer');

insert into dem.occupation (name) values ('student');
insert into dem.occupation (name) values ('teacher');
insert into dem.occupation (name) values ('lecturer');
insert into dem.occupation (name) values ('mechanic');
insert into dem.occupation (name) values ('cleaner');
insert into dem.occupation (name) values ('engineer');
insert into dem.occupation (name) values ('hairdresser');
insert into dem.occupation (name) values ('unemployed');
insert into dem.occupation (name) values ('scientist');
insert into dem.occupation (name) values ('retired');
insert into dem.occupation (name) values ('dentist');
insert into dem.occupation (name) values ('police officer');
insert into dem.occupation (name) values ('soldier');
insert into dem.occupation (name) values ('security guard');
insert into dem.occupation (name) values ('farmer');
insert into dem.occupation (name) values ('unknown');

insert into dem.enum_ext_id_types (name, issuer, context) values ('Medicare', 'HIC', 'p');
insert into dem.enum_ext_id_types (name, issuer, context) values ('Provider No.', 'HIC', 'c');
insert into dem.enum_ext_id_types (name, issuer, context) values ('Prescriber No.', 'HIC', 'c');
insert into dem.enum_ext_id_types (name, issuer, context) values ('DVA', 'Department of Veteran''s Affairs', 'p');
insert into dem.enum_ext_id_types (name, issuer, context) values ('CRN', 'Centrelink', 'p');
insert into dem.enum_ext_id_types (name, issuer, context) values ('Licence No.', 'RTA', 'p');
insert into dem.enum_ext_id_types (name, issuer, context) values ('ABN', 'ATO', 'o');
insert into dem.enum_ext_id_types (name, issuer, context) values ('ACN', 'ATO', 'o');
INSERT INTO dem.enum_ext_id_types (name, issuer, context) VALUES ('MPBV Reg No', 'Medical Practice Board of Victoria', 'p');
INSERT INTO dem.enum_ext_id_types (name, issuer, context) VALUES ('ur_no', 'dbf importer type au-md v0.1', 'p');
--insert into dem.enum_ext_id_types (name, issuer, context) values ('', '', '');


-- ===================================================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename='$RCSfile: gmDemographics.au.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmDemographics.au.sql,v $', '$Revision: 1.15 $');

-- ===================================================================
-- $Log: gmDemographics.au.sql,v $
-- Revision 1.15  2006-07-04 14:18:04  ncq
-- - add two ext id types
--
-- Revision 1.14  2006/01/06 10:12:02  ncq
-- - add missing grants
-- - add_table_for_audit() now in "audit" schema
-- - demographics now in "dem" schema
-- - add view v_inds4vaccine
-- - move staff_role from clinical into demographics
-- - put add_coded_term() into "clin" schema
-- - put German things into "de_de" schema
--
-- Revision 1.13  2005/09/19 16:38:51  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.12  2005/07/14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.11  2004/06/17 11:31:07  ihaywood
-- A new form template for the new form markup.
-- Basically @...@ where any Python expression can exist
-- between the "@" signs. The other form templates will be changed over eventually.
--
-- Revision 1.10  2004/03/04 19:41:52  ncq
-- - whitespace, comment
--
-- Revision 1.9  2004/03/04 10:48:06  ncq
-- - don't hardcode primary keys for ext_id_types
--
-- Revision 1.8  2004/03/03 23:50:58  ihaywood
-- external ID types for Australia.
--
-- Revision 1.7  2004/03/02 10:22:41  ihaywood
-- support for martial status and occupations
-- .conf files now use host autoprobing
--
-- Revision 1.6  2004/01/05 00:59:14  ncq
-- - remove ourselves from schema revision table
--
-- Revision 1.5  2003/12/29 15:49:46  uid66147
-- - reset client_encoding
--
-- Revision 1.4  2003/10/01 16:12:01  ncq
-- - AU -> au
--
-- Revision 1.3  2003/10/01 15:45:20  ncq
-- - use add_table_for_audit() instead of inheriting from audit_mark
--
-- Revision 1.2  2003/08/17 00:27:33  ncq
-- - log_ tables removed, now auto-created
--
-- Revision 1.1  2003/08/05 09:24:51  ncq
-- - first checkin
--
