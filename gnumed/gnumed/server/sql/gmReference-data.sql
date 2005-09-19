-- ===================================================
-- GnuMed reference data

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmReference-data.sql,v $
-- $Revision: 1.4 $

-- ===================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================
-- paper sizes taken from the GhostScript man pages
insert into papersizes (name, size) values ('A0', '(83.9611, 118.816)');
insert into papersizes (name, size) values ('A1', '(59.4078, 83.9611)');
insert into papersizes (name, size) values ('A2', '(41.9806, 59.4078)');
insert into papersizes (name, size) values ('A3', '(29.7039, 41.9806)');
insert into papersizes (name, size) values ('A4', '(20.9903, 29.7039)');
insert into papersizes (name, size) values ('A5', '(14.8519, 20.9903)');
insert into papersizes (name, size) values ('A6', '(10.4775, 14.8519)');
insert into papersizes (name, size) values ('A7', '(7.40833, 10.4775)');
insert into papersizes (name, size) values ('A8', '(5.22111, 7.40833)');
insert into papersizes (name, size) values ('A9', '(3.70417, 5.22111)');
insert into papersizes (name, size) values ('A10', '(2.61056, 3.70417)');
insert into papersizes (name, size) values ('B0', '(100.048, 141.393)');
insert into papersizes (name, size) values ('B1', '(70.6967 ,100.048)');
insert into papersizes (name, size) values ('B2', '(50.0239,70.6967)');
insert into papersizes (name, size) values ('B3', '(35.3483,50.0239)');
insert into papersizes (name, size) values ('B4', '(25.0119,35.3483)');
insert into papersizes (name, size) values ('B5', '(17.6742,25.0119)');
insert into papersizes (name, size) values ('archA', '(22.86,30.48)');
insert into papersizes (name, size) values ('archB', '(30.48,45.72)');
insert into papersizes (name, size) values ('archC', '(45.72,60.96)');
insert into papersizes (name, size) values ('archD', '(60.96,91.44)');
insert into papersizes (name, size) values ('archE', '(91.44,121.92)');
insert into papersizes (name, size) values ('flsa', '(21.59,33.02)');
insert into papersizes (name, size) values ('flse', '(21.59,33.02)');
insert into papersizes (name, size) values ('halfletter', '(13.97,21.59)');
insert into papersizes (name, size) values ('note', '(19.05,  25.4)');
insert into papersizes (name, size) values ('letter', '(21.59, 27.94)');
insert into papersizes (name, size) values ('legal', '(21.59, 35.56)');
insert into papersizes (name, size) values ('11x17', '(27.94, 43.18)');
insert into papersizes (name, size) values ('ledger', '(43.18, 27.94)');

-- ===================================================
-- form templates
-- ===================================================

insert into form_field_types (name) values ('string');
-- plain text, param is a regex which must match 
-- after every keypress during editing, to
-- instantly reject erroneous input
-- regexes must therefore match partial valid inputs, including
-- the empty string
-- [0-9]*            integer
-- [0-9,]*\.?[0-9]*  float
-- [0-9]{0,7}|([0-9]{6,7}[A-Z])  HIC provider number
-- [a-zA-Z]?[a-zA-Z0-9]*\@?[a-zA-Z0-9\.]* email address 
-- SINGLE LINE ONLY !
insert into form_field_types (name) values ('list');
-- FIXME: this does not work, we may not know the list before runtime
-- one selected from a list of string values, param is the list, 
-- separated by '\n'.
-- whether this is displayed as radio buttons, drop down list, &c, is
-- up to the GUI layer.
insert into form_field_types (name) values ('boolean');
-- boolean value. GUI will usually be some form of tickbox
insert into form_field_types (name) values ('text');
-- a larger piece of text. This suggests the GUI element should be multi-line
-- and have word-processing features like spellcheck. 
-- maybe allow some simple markup like bold and italic text
insert into form_field_types (name) values ('date');
-- a date

-- FIXME: I have serious doubts this will work but let's give it a try
insert into form_field_types (name) values ('entity');
-- a gmDemographicRecord.cOrg or its descendant (cIdentity). Usually the
-- addressee of a communication (but doesn't have to be)
insert into form_field_types (name) values ('address');
-- an address of the entity (an entity field must be in the form too,
-- param is the internal_name of this field)
-- this is a Python dict with fields 'number', 'street', 'addendum', 'city', 'postcode'
insert into form_field_types (name) values ('drug_list');
-- a list of drug-preparations, business layer class yet to be written

-- ===================================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename='$RCSfile: gmReference-data.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmReference-data.sql,v $', '$Revision: 1.4 $');

-- ===================================================
-- $Log: gmReference-data.sql,v $
-- Revision 1.4  2005-09-19 16:38:51  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.3  2005/07/14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.2  2005/01/24 17:57:43  ncq
-- - cleanup
-- - Ian's enhancements to address and forms tables
--
-- Revision 1.1  2004/03/09 09:21:56  ncq
-- - paper sizes
--
