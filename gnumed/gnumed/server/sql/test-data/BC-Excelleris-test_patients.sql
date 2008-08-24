-- Project GNUmed

-- test patients from British Columbia, Excelleris Labs, HL7 import

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
--
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/test-data/BC-Excelleris-test_patients.sql,v $
-- $Revision: 1.1 $
-- =============================================

-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

set default_transaction_read_only to off;

begin;

-- =============================================
select dem.add_external_id_type('PHN', 'BC Medical Services Plan, CA', 'p');
select dem.add_external_id_type('medical record number', 'fake hospital 1 in BC, CA', 'p');
select dem.add_external_id_type('medical record number', 'fake hospital 2 in BC, CA', 'p');

-- =============================================
-- "APATIENT"

-- identity
insert into dem.identity (gender, dob, cob)
values ('m', '19770726 02:01-7:00', 'CA');

-- name
insert into dem.names (id_identity, active, lastnames, firstnames, comment)
values (
	currval(pg_get_serial_sequence('dem.identity', 'pk')),
	--currval('dem.identity_pk_seq'),
	true, 'BC_BROKER', 'APATIENT', 'CA::BC::Excelleris test patient A'
);

-- =============================================
-- "BPATIENT"

-- identity
insert into dem.identity (gender, dob, cob)
values ('f', '1943-01-02 02:01-7:00', 'CA');

-- name
insert into dem.names (id_identity, active, lastnames, firstnames, comment)
values (
	currval(pg_get_serial_sequence('dem.identity', 'pk')),
	--currval('dem.identity_pk_seq'),
	true, 'BC_BROKER', 'BPATIENT', 'CA::BC::Excelleris test patient B'
);

-- Personal Health Number
insert into dem.lnk_identity2ext_id (id_identity, external_id, fk_origin)
values (
	currval(pg_get_serial_sequence('dem.identity', 'pk')),
	--currval('dem.identity_pk_seq'),
	'9012345678',
	(select pk from dem.enum_ext_id_types where name = 'PHN' and issuer = 'BC Medical Services Plan, CA')
);

-- external record number(s)
insert into dem.lnk_identity2ext_id (id_identity, external_id, fk_origin)
values (
	currval(pg_get_serial_sequence('dem.identity', 'pk')),
	--currval('dem.identity_pk_seq'),
	'3585370',
	(select pk from dem.enum_ext_id_types where name = 'medical record number' and issuer = 'fake hospital 1 in BC, CA')
);

insert into dem.lnk_identity2ext_id (id_identity, external_id, fk_origin)
values (
	currval(pg_get_serial_sequence('dem.identity', 'pk')),
	--currval('dem.identity_pk_seq'),
	'3103392',
	(select pk from dem.enum_ext_id_types where name = 'medical record number' and issuer = 'fake hospital 2 in BC, CA')
);

-- =============================================
-- "CPATIENT"

-- identity
insert into dem.identity (gender, dob, cob)
values ('f', '19240817 02:01-7:00', 'CA');

-- name
insert into dem.names (id_identity, active, lastnames, firstnames, comment)
values (
	currval(pg_get_serial_sequence('dem.identity', 'pk')),
	--currval('dem.identity_pk_seq'),
	true, 'BC_BROKER', 'CPATIENT', 'CA::BC::Excelleris test patient C'
);

-- =============================================
-- "DPATIENT"

-- identity
insert into dem.identity (gender, dob, cob)
values ('m', '19680612 02:01-7:00', 'CA');

-- name
insert into dem.names (id_identity, active, lastnames, firstnames, comment)
values (
	currval(pg_get_serial_sequence('dem.identity', 'pk')),
	--currval('dem.identity_pk_seq'),
	true, 'BC_BROKER', 'DPATIENT', 'CA::BC::Excelleris test patient D'
);

-- =============================================
-- "EPATIENT"

-- identity
insert into dem.identity (gender, dob, cob)
values ('f', '19890214 02:01-7:00', 'CA');

-- name
insert into dem.names (id_identity, active, lastnames, firstnames, comment)
values (
	currval(pg_get_serial_sequence('dem.identity', 'pk')),
	--currval('dem.identity_pk_seq'),
	true, 'BC_BROKER', 'EPATIENT', 'CA::BC::Excelleris test patient E'
);

-- =============================================
-- "FPATIENT"

-- identity
insert into dem.identity (gender, dob, cob)
values ('f', '19210523 02:01-7:00', 'CA');

-- name
insert into dem.names (id_identity, active, lastnames, firstnames, comment)
values (
	currval(pg_get_serial_sequence('dem.identity', 'pk')),
	--currval('dem.identity_pk_seq'),
	true, 'BC_BROKER', 'FPATIENT', 'CA::BC::Excelleris test patient F'
);

-- =============================================
-- "GPATIENT"

-- identity
insert into dem.identity (gender, dob, cob)
values ('m', '19750926 02:01-7:00', 'CA');

-- name
insert into dem.names (id_identity, active, lastnames, firstnames, comment)
values (
	currval(pg_get_serial_sequence('dem.identity', 'pk')),
	--currval('dem.identity_pk_seq'),
	true, 'BC_BROKER', 'GPATIENT', 'CA::BC::Excelleris test patient G'
);

-- external record number(s)
insert into dem.lnk_identity2ext_id (id_identity, external_id, fk_origin)
values (
	currval(pg_get_serial_sequence('dem.identity', 'pk')),
	--currval('dem.identity_pk_seq'),
	'MM00000256',
	(select pk from dem.enum_ext_id_types where name = 'medical record number' and issuer = 'fake hospital 1 in BC, CA')
);

insert into dem.lnk_identity2ext_id (id_identity, external_id, fk_origin)
values (
	currval(pg_get_serial_sequence('dem.identity', 'pk')),
	--currval('dem.identity_pk_seq'),
	'AB00000256',
	(select pk from dem.enum_ext_id_types where name = 'medical record number' and issuer = 'fake hospital 2 in BC, CA')
);

-- =============================================
-- do simple schema revision tracking
select gm.log_script_insertion('$RCSfile: BC-Excelleris-test_patients.sql,v $', '$Revision: 1.1 $');

-- comment out the "rollback" if you want to
-- really store the above patient data
rollback;
commit;

-- =============================================
-- $Log: BC-Excelleris-test_patients.sql,v $
-- Revision 1.1  2008-08-24 14:30:41  ncq
-- - Canadian lab test patients
--
--
