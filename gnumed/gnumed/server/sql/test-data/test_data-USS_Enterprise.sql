-- Projekt GnuMed
-- USS Enterprise defs
-- http://www.nimoy.com/spock.html

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/test-data/test_data-USS_Enterprise.sql,v $
-- $Revision: 1.3 $
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
-- pathology lab
insert into test_org
	(fk_org, fk_adm_contact, fk_med_contact, internal_name, comment)
values (
	99999,
	(select i_id from v_basic_person where firstnames='Leonard' and lastnames='Spock' and dob='1931-3-26'::timestamp),
	(select i_id from v_basic_person where firstnames='Leonard' and lastnames='McCoy' and dob='1920-1-20'::timestamp),
	'Enterprise Main Lab',
	'the main path lab aboard the USS Enterprise'
);

-- tests
insert into test_type
	(fk_test_org, code, name, comment, basic_unit)
values (
	currval('test_org_pk_seq'),
	'WBC',
	'leukocytes',
	'EDTA sample',
	'Gpt/l'
);

insert into test_type
	(fk_test_org, code, name, comment, basic_unit)
values (
	currval('test_org_pk_seq'),
	'RBC',
	'erythrocytes',
	'EDTA sample',
	'Tpt/l'
);

insert into test_type
	(fk_test_org, code, name, comment, basic_unit)
values (
	currval('test_org_pk_seq'),
	'PLT',
	'platelets',
	'EDTA sample',
	'Gpt/l'
);

insert into test_type
	(fk_test_org, code, name, comment, basic_unit)
values (
	currval('test_org_pk_seq'),
	'CRP',
	'C-reactive protein',
	'blood serum',
	'mg/l'
);

-- =============================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename like '$RCSfile: test_data-USS_Enterprise.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: test_data-USS_Enterprise.sql,v $', '$Revision: 1.3 $');

-- =============================================
-- $Log: test_data-USS_Enterprise.sql,v $
-- Revision 1.3  2004-03-18 18:32:09  ncq
-- - thrombocytes -> platelets
--
-- Revision 1.2  2004/03/18 10:29:51  ncq
-- - set fk_org on EML to 99999
--
-- Revision 1.1  2004/03/18 10:22:25  ncq
-- - Enterprise path lab
--
