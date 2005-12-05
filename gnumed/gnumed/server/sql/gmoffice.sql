-- GNUmed office related/administrative tables

-- This is free software in the sense of the General Public License (GPL)
-- For details regarding GPL licensing see http://gnu.org

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmoffice.sql,v $
-- $Revision: 1.15 $ $Date: 2005-12-05 16:17:24 $ $Author: ncq $
-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
-- forms handling
-- ===================================================================
-- queue types
create table form_job_targets (
	pk serial
		primary key,
	target text
		unique
		not null
);

comment on table form_job_targets is
	'the form job targets (eg. printers, faxes, smtp servers) in
	 whatever granularity is needed locally, can be used for load
	 balancing/round robin servicing busy queues';

-- -------------------------------------------------------------------
-- queue of forms pending for processing
create table form_job_queue (
	pk serial primary key,
	fk_form_instance integer
		not null
		references clin.form_instances(pk),
	form bytea
		not null,
	fk_job_target integer
		not null
		references form_job_targets(pk),
	submitted_when timestamp with time zone
		not null
		default CURRENT_TIMESTAMP,
	fk_submitted_by integer
		not null,
	submitted_from text
		not null,
	status text
		not null
		default 'submitted'
);

-- FIXME: we need a trigger that allows UPDATEs on "status" only
-- FIXME: we also need a notify trigger on insert/update

--select add_x_db_fk_def('form_job_queue', 'fk_submitted_by', 'personalia', 'staff', 'pk');

comment on table form_job_queue is
	'Queue table for rendered form instances. Note that
	 the rows in this table will get deleted after processing.
	 This is NOT an archive of form jobs.';
comment on column form_job_queue.fk_form_instance is
	'points to the unrendered source instance of the form,
	 useful for recalling submitted jobs for changing';
comment on column form_job_queue.form is
	'the rendered form, IOW binary data such as a PDF file';
comment on column form_job_queue.fk_job_target is
	'points to the job target';
comment on column form_job_queue.submitted_when is
	'when was this form job submitted';
comment on column form_job_queue.fk_submitted_by is
	'who of the staff submitted this form job';
comment on column form_job_queue.submitted_from is
	'the workplace this form job was submitted from';
comment on column form_job_queue.status is
	'status of the form job:
	 - submitted: ready for processing
	 - in progress: being processed
	 - removable: fit for removal (either cancelled, timed out or done)
	 - halted: do not process';

-- ===================================================================


-- ===================================================================
-- Embryo of billing tables
-- This is a highly classical accounting system, with medical-specific
-- updatable views.

--create table schedule (
--	id serial primary key,
--	code text,
--	name text,
--	min_duration integer,
--	description text
--);

--create table billing_scheme (
--	id serial primary key,
--	name text,
--	iso_countrycode char (2)
--);

--create table prices (
--	id_consult integer references schedule (id),
--	id_scheme integer references billing_scheme (id),
--	patient float,
--	bulkbill float
--);

--comment on column prices.patient is
--	'the amount of money paid by the patient';
--comment on column prices.bulkbill is
--	'the amount billed directly (bulk-billed) to the payor';

--create table accounts (
--	id serial primary key,
--	name text,
--	extra integer
--);

--alter table accounts add column parent integer references accounts (id);

--create table ledger (
--	stamp timestamp,
--	amount float,
--	debit integer references accounts (id),
--	credit integer references accounts (id)
--);

--create table consults
--(
--	start timestamp,
--	finish timestamp,
--	id_location integer,
--	id_doctor integer,
--	id_patient integer,
--	id_type integer references schedule (id),
--	id_scheme integer references billing_scheme (id)
--);

-- ===================================================================
-- permissions
-- ===================================================================
GRANT SELECT ON
	form_job_targets
	, form_job_queue
TO GROUP "gm-public";

GRANT select, insert, delete, update ON
	form_job_queue
	, form_job_queue_pk_seq
TO GROUP "gm-doctors";

-- ===================================================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename='$RCSfile: gmoffice.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmoffice.sql,v $', '$Revision: 1.15 $');

--=====================================================================
-- $Log: gmoffice.sql,v $
-- Revision 1.15  2005-12-05 16:17:24  ncq
-- - remove calls to add_x_db_*
--
-- Revision 1.14  2005/11/25 15:07:28  ncq
-- - create schema "clin" and move all things clinical into it
--
-- Revision 1.13  2005/09/22 15:38:21  ncq
-- - cleanup
--
-- Revision 1.12  2005/09/19 16:38:51  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.11  2005/07/14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.10  2005/03/01 20:38:19  ncq
-- - varchar -> text
--
-- Revision 1.9  2005/01/29 18:45:22  ncq
-- - form_target_classes -> form_job_targets
-- - form_queue -> form_job_queue
--
-- Revision 1.8  2005/01/12 12:29:29  ncq
-- - comment out some unused tables
--
-- Revision 1.7  2004/07/17 20:57:53  ncq
-- - don't use user/_user workaround anymore as we dropped supporting
--   it (but we did NOT drop supporting readonly connections on > 7.3)
--
-- Revision 1.6  2004/03/23 22:43:46  ncq
-- - 7.4 is stricter about FKs having to point to unique references
--
-- Revision 1.5  2004/03/10 15:45:15  ncq
-- - grants on form tables
--
-- Revision 1.4  2004/03/10 00:08:31  ncq
-- - add form queue handling
-- - remove papersizes
-- - cleanup
--
-- Revision 1.3  2002/12/14 08:12:22  ihaywood
-- New prescription tables in gmclinical.sql
--
-- Revision 1.2  2002/12/06 08:50:52  ihaywood
-- SQL internationalisation, gmclinical.sql now internationalised.
--
-- Revision 1.1  2002/12/03 02:50:19  ihaywood
-- new office schema: tables for printing forms
