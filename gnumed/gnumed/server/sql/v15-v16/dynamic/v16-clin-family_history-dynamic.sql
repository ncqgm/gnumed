-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on table clin.family_history is
	'This table stores family history items on persons not otherwise in the database.';


select audit.register_table_for_auditing('clin', 'family_history');
select gm.register_notifying_table('clin', 'family_history');


grant select, insert, update, delete on clin.family_history to group "gm-doctors";
grant usage on clin.clin_hx_family_pk_seq to group "gm-doctors";


delete from audit.audited_tables where
	schema = 'clin'
		and
	table_name = 'clin_hx_family'
;

\unset ON_ERROR_STOP
drop function audit.ft_del_clin_hx_family() cascade;
drop function audit.ft_ins_clin_hx_family() cascade;
drop function audit.ft_upd_clin_hx_family() cascade;
\set ON_ERROR_STOP 1


delete from audit.audited_tables where
	schema = 'clin'
		and
	table_name = 'hx_family_item'
;

-- --------------------------------------------------------------
comment on column clin.family_history.clin_when is
	'When the family history item became known to the patient (not the afflicted relative).';

-- --------------------------------------------------------------
comment on column clin.family_history.soap_cat is NULL;

-- --------------------------------------------------------------
comment on column clin.family_history.fk_relation_type is
	'foreign key to the type of relation the patient has to the afflicated relative';

\unset ON_ERROR_STOP
alter table clin.family_history drop constraint family_history_fk_relation_type_fkey cascade;
\set ON_ERROR_STOP 1

alter table clin.family_history
	add foreign key (fk_relation_type)
		references clin.fhx_relation_type(pk)
		on update cascade
		on delete restrict;

alter table clin.family_history
	alter column fk_relation_type
		set not null;

-- --------------------------------------------------------------
-- .name_relative
comment on column clin.family_history.name_relative is
	'name of the relative suffering the condition';

\unset ON_ERROR_STOP
alter table clin.family_history drop constraint c_family_history_sane_name cascade;
\set ON_ERROR_STOP 1

alter table clin.family_history
	add constraint c_family_history_sane_name
		check (gm.is_null_or_non_empty_string(name_relative) is True);

-- --------------------------------------------------------------
-- .dob_relative
comment on column clin.family_history.dob_relative is
	'date of birth of the relative if known';

-- --------------------------------------------------------------
comment on column clin.family_history.narrative is
	'the condition this relative suffered from';

\unset ON_ERROR_STOP
alter table clin.family_history drop constraint c_family_history_sane_condition cascade;
\set ON_ERROR_STOP 1

alter table clin.family_history
	add constraint c_family_history_sane_condition
		check (gm.is_null_or_blank_string(narrative) is False);

-- --------------------------------------------------------------
-- .age_noted
comment on column clin.family_history.age_noted is
	'age at which the condition was noted in the relative if known';

\unset ON_ERROR_STOP
alter table clin.family_history drop constraint c_family_history_sane_age_noted cascade;
\set ON_ERROR_STOP 1

alter table clin.family_history
	add constraint c_family_history_sane_age_noted
		check (gm.is_null_or_non_empty_string(age_noted) is True);

-- --------------------------------------------------------------
-- .age_of_death
comment on column clin.family_history.age_of_death is
	'age at which the relative died if known';

--\unset ON_ERROR_STOP
--alter table clin.family_history drop constraint c_family_history_sane_age_of_death cascade;
--\set ON_ERROR_STOP 1

--alter table clin.family_history
--	add constraint c_family_history_sane_age_of_death
--		check (gm.is_null_or_non_empty_string(age_of_death) is True);


--\unset ON_ERROR_STOP
--alter table clin.family_history drop constraint c_family_history_sane_death_age cascade;
--\set ON_ERROR_STOP 1

--alter table clin.family_history
--	add constraint c_family_history_sane_death_age
--		check (age_of_death >= age_of_onset);

-- --------------------------------------------------------------
-- .contributed_to_death
comment on column clin.family_history.contributed_to_death is
	'whether the condition contributed to the death of the relative if known';

alter table clin.family_history
	alter column contributed_to_death
		set default null;

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-family_history-dynamic.sql', 'v16.0');
