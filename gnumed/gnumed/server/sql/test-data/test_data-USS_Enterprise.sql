-- Projekt GnuMed
-- USS Enterprise defs

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/test-data/test_data-USS_Enterprise.sql,v $
-- $Revision: 1.9 $
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
-- pathology lab
insert into test_org
	(fk_org, fk_adm_contact, fk_med_contact, internal_name, comment)
values (
	99999,
	(select i_id from v_basic_person where firstnames='Leonard' and lastnames='Spock' and dob='1931-3-26+2:00'::timestamp),
	(select i_id from v_basic_person where firstnames='Leonard' and lastnames='McCoy' and dob='1920-1-20+2:00'::timestamp),
	'Enterprise Main Lab',
	'the main path lab aboard the USS Enterprise'
);

-- tests
insert into test_type
	(fk_test_org, code, name, comment, basic_unit)
values (
	currval('test_org_pk_seq'),
	'WBC-EML',
	'leukocytes (EML)',
	'EDTA sample',
	'Gpt/l'
);

insert into test_type_local
	(fk_test_type, local_code, local_name)
values (
	currval('test_type_id_seq'),
	'WBC',
	'leukocytes'
);

insert into test_type
	(fk_test_org, code, name, comment, basic_unit)
values (
	currval('test_org_pk_seq'),
	'RBC-EML',
	'erythrocytes (EML)',
	'EDTA sample',
	'Tpt/l'
);

insert into test_type_local
	(fk_test_type, local_code, local_name)
values (
	currval('test_type_id_seq'),
	'RBC',
	'erythrocytes'
);

insert into test_type
	(fk_test_org, code, name, comment, basic_unit)
values (
	currval('test_org_pk_seq'),
	'PLT-EML',
	'platelets (EML)',
	'EDTA sample',
	'Gpt/l'
);

insert into test_type_local
	(fk_test_type, local_code, local_name)
values (
	currval('test_type_id_seq'),
	'PLT',
	'platelets'
);

insert into test_type
	(fk_test_org, code, name, comment, basic_unit)
values (
	currval('test_org_pk_seq'),
	'CRP-EML',
	'C-reactive protein (EML)',
	'blood serum',
	'mg/l'
);

insert into test_type_local
	(fk_test_type, local_code, local_name)
values (
	currval('test_type_id_seq'),
	'CRP',
	'C-reactive protein'
);

-- =============================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename like '$RCSfile: test_data-USS_Enterprise.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: test_data-USS_Enterprise.sql,v $', '$Revision: 1.9 $');

-- =============================================
-- $Log: test_data-USS_Enterprise.sql,v $
-- Revision 1.9  2004-06-02 14:41:18  ncq
-- - remove offending set time zone statement
--
-- Revision 1.8  2004/06/02 13:46:46  ncq
-- - setting default session timezone has incompatible syntax
--   across version range 7.1-7.4, henceforth specify timezone
--   directly in timestamp values, which works
--
-- Revision 1.7  2004/06/02 00:14:47  ncq
-- - add time zone setting
--
-- Revision 1.6  2004/05/06 23:32:44  ncq
-- - internal_name now local_name
-- - technically_abnormal now text
--
-- Revision 1.5  2004/03/23 17:34:50  ncq
-- - support and use optionally cross-provider unified test names
--
-- Revision 1.4  2004/03/19 11:56:59  ncq
-- - remove misleading URL
--
-- Revision 1.3  2004/03/18 18:32:09  ncq
-- - thrombocytes -> platelets
--
-- Revision 1.2  2004/03/18 10:29:51  ncq
-- - set fk_org on EML to 99999
--
-- Revision 1.1  2004/03/18 10:22:25  ncq
-- - Enterprise path lab
--
