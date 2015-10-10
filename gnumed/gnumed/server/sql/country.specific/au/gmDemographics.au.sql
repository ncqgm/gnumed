-- Project: GNUmed
-- ===================================================================
-- license: GPL v2 or later
-- authors: Ian Haywood, Horst Herb, Karsten Hilbert, Richard Terry

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

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
