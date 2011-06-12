-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on table clin.fhx_relation_type is
	'Enumerates inter-person relations for family history linking.';


select audit.register_table_for_auditing('clin', 'fhx_relation_type');


grant select, insert, update, delete on
	clin.fhx_relation_type
to group "gm-doctors";

grant usage on clin.fhx_relation_type_pk_seq to group "gm-doctors";

-- --------------------------------------------------------------
comment on column clin.fhx_relation_type.description is
	'Description of the relation type, specific or unspecific: sister, father, ..., maternal family, ...';

\unset ON_ERROR_STOP
alter table clin.fhx_relation_type drop constraint c_fhx_relation_type_sane_desc cascade;
\set ON_ERROR_STOP 1

alter table clin.fhx_relation_type
	add constraint c_fhx_relation_type_sane_desc
		check (gm.is_null_or_blank_string(description) is False);

-- --------------------------------------------------------------
comment on column clin.fhx_relation_type.is_genetic is
'Whether or not this type of relation is biologic/genetic or not. Note that non-genetic relations may still pose a risk because of infectious diseases.';

alter table clin.fhx_relation_type
	alter column is_genetic
		set not null;

alter table clin.fhx_relation_type
	alter column is_genetic
		set default True;

-- --------------------------------------------------------------
alter table clin.fhx_relation_type
	add constraint c_fhx_rel_type_uniq
		unique(description, is_genetic);

-- --------------------------------------------------------------
INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'General  History (maternal)'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'General  History (maternal)'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'General History (paternal)'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'General History (paternal)'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'great grandfather (paternal)'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'great grandfather (paternal)'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'great grandfather (maternal)'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'great grandfather (maternal)'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'great grandmother (maternal)'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'great grandmother (maternal)'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'great grandmother (paternal)'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'great grandmother (paternal)'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'defacto wife'::text,
		False
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'defacto wife'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'adopted daughter'::text,
		False
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'adopted daughter'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'adopted son'::text,
		False
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'adopted son'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'adoptive mother'::text,
		False
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'adoptive mother'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'adoptive father'::text,
		False
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'adoptive father'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'grandson'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'grandson'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'granddaughter'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'granddaughter'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'grandfather'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'grandfather'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'grandmother'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'grandmother'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'cousin'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'cousin'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'cousin'::text,
		False
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'cousin'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'aunt'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'aunt'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'aunt'::text,
		False
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'aunt'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'uncle'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'uncle'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'uncle'::text,
		False
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'uncle'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'defacto husband'::text,
		False
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'defacto husband'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'cousin (paternal)'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'cousin (paternal)'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'cousin (paternal)'::text,
		False
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'cousin (paternal)'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'cousin (maternal)'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'cousin (maternal)'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'cousin (maternal)'::text,
		False
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'cousin (maternal)'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'General Family History'::text,
		False
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'General Family History'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'step daughter'::text,
		False
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'step daughter'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'daughter'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'daughter'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'step son'::text,
		False
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'step son'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'son'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'son'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'nephew'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'nephew'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'stepnephew'::text,
		False
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'stepnephew'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'uncle (paternal)'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'uncle (paternal)'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'uncle (maternal)'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'uncle (maternal)'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'defacto'::text,
		False
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'defacto'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'husband'::text,
		False
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'husband'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'wife'::text,
		False
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'wife'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'grandfather (paternal)'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'grandfather (paternal)'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'grandfather (maternal)'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'grandfather (maternal)'
	);


INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'grandmother (paternal)'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'grandmother (paternal)'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'grandmother (maternal)'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'grandmother (maternal)'
	);


INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'niece'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'niece'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'niece'::text,
		False
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'niece'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'aunt (paternal)'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'aunt (paternal)'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'aunt (maternal)'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'aunt (maternal)'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'sister'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'sister'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'brother'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'brother'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'Step father'::text,
		False
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'step father'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'father'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'father'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'step mother'::text,
		False
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'step mother'
	);

INSERT INTO clin.fhx_relation_type (
	description,
	is_genetic
)	SELECT
		'mother'::text,
		True
	WHERE NOT EXISTS (
		SELECT 1 FROM clin.fhx_relation_type
		WHERE
			description = 'mother'
	);

-- --------------------------------------------------------------
-- --------------------------------------------------------------
comment on table clin.family_history is
	'This table stores family history items on persons not otherwise in the database.';


select audit.register_table_for_auditing('clin', 'fhx_relation_type');
select gm.register_notifying_table('clin', 'family_history');


grant select, insert, update, delete on
	clin.family_history
to group "gm-doctors";

grant usage on clin.clin_hx_family_pk_seq to group "gm-doctors";

delete from audit.audited_tables where
	schema = 'clin'
		and
	table_name = 'hx_family_item'
;

delete from audit.audited_tables where
	schema = 'clin'
		and
	table_name = 'clin_hx_family'
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
