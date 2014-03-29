-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

--set default_transaction_read_only to off;
set check_function_bodies to on;

-- --------------------------------------------------------------
comment on table clin.patient is 'A table to hold unique-per-identity *clinical* items, such as Expected Due Date.';


select gm.register_notifying_table('clin', 'patient');
select audit.register_table_for_auditing('clin', 'patient');


revoke all on clin.patient from "public";
--grant select on clin.patient to group "gm-staff";
grant select, insert, update, delete on clin.patient to group "gm-doctors";


GRANT USAGE ON SEQUENCE
	clin.patient_pk_seq
to group "gm-doctors";


-- --------------------------------------------------------------
-- .fk_identity
comment on column clin.patient.fk_identity is 'the dem.identity.pk of this patient';

alter table clin.patient
	alter column fk_identity
		set not null;


alter table clin.patient drop constraint if exists FK_clin_patient_fk_identity cascade;

alter table clin.patient
	add constraint FK_clin_patient_fk_identity foreign key (fk_identity)
		references dem.identity(pk)
		on update cascade
		on delete cascade
;


alter table clin.patient drop constraint if exists clin_patient_uniq_fk_identity cascade;

alter table clin.patient
	add constraint clin_patient_uniq_fk_identity unique (fk_identity);

-- --------------------------------------------------------------
-- .edc
comment on column clin.patient.fk_identity is 'the dem.identity.pk of this patient';


alter table clin.patient
	alter column edc
		set default null;


-- helper functions
create or replace function clin.get_dob(integer)
	returns timestamp with time zone
	language sql
	as '
		select date_trunc(''day''::text, d_i.dob) + COALESCE(d_i.tob, d_i.dob::time without time zone)::interval AS dob
		from dem.identity d_i
		where d_i.pk = $1;
	';

revoke all on function clin.get_dob(integer) from public;
grant execute on function clin.get_dob(integer) to "gm-public";


create or replace function clin.get_dod(integer)
	returns timestamp with time zone
	language sql
	as 'select deceased from dem.identity d_i where d_i.pk = $1;';

revoke all on function clin.get_dod(integer) from public;
grant execute on function clin.get_dod(integer) to "gm-public";


--create or replace function clin.get_gender(integer)
--	returns text
--	language sql
--	as 'select gender from dem.identity d_i where d_i.pk = $1;';

--revoke all on function clin.get_gender(integer) from public;
--grant execute on function clin.get_gender(integer) to "gm-public";


-- constraint
alter table clin.patient drop constraint if exists clin_patient_sane_edc cascade;

alter table clin.patient
	add constraint clin_patient_sane_edc check (
		(edc IS NULL)
			or
		(
--			(clin.get_gender(fk_identity) IN ('f', 'tf', 'tm', 'h'))
--				and
			(clin.get_dod(fk_identity) IS NULL)
				and
			(
				(clin.get_dob(fk_identity) IS NULL)
					or
				(edc > clin.get_dob(fk_identity) + '5 years'::interval)
			)
		)
	);

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-clin-patient-dynamic.sql', '20.0');
