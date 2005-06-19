-- Project: GnuMed
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmclinical.sql,v $
-- $Revision: 1.160 $
-- license: GPL
-- author: Ian Haywood, Horst Herb, Karsten Hilbert

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
create table xlnk_identity (
	pk serial primary key,
	xfk_identity integer unique not null,
	pupic text unique not null,
	data text unique default null
) inherits (audit_fields);

select add_x_db_fk_def('xlnk_identity', 'xfk_identity', 'personalia', 'identity', 'pk');
select add_table_for_audit('xlnk_identity');

comment on table xlnk_identity is
	'this is the one table with the unresolved identity(pk)
	 foreign key, all other tables in this service link to
	 this table, depending upon circumstances one can add
	 dblink() verification or a true FK constraint (if "personalia"
	 is in the same database as "historica")';

-- ===================================================================
-- generic EMR structure
-- ===================================================================
-- health issue tables
create table clin_health_issue (
	id serial primary key,
	id_patient integer
		not null
		references xlnk_identity(xfk_identity)
		on update cascade
		on delete restrict,
	description text
		not null
		default null,
	age_noted interval
		default null,
	is_active boolean
		default true,
	clinically_relevant boolean
		default true,
	is_confidential boolean
		default false,
	is_cause_of_death boolean
		not null
		default false,
	unique (id_patient, description)
) inherits (audit_fields);

alter table clin_health_issue add constraint issue_name_not_empty
	check (trim(both from description) != '');

select add_table_for_audit('clin_health_issue');

-- FIXME: Richard also has is_operation, laterality

comment on table clin_health_issue is
	'this is pretty much what others would call "Past Medical History",
	 eg. longer-ranging, underlying, encompassing issues with one''s
	 health such as "mild immunodeficiency", "diabetes type 2",
	 in Belgium it is called "problem",
	 L.L.Weed includes lots of little things into it, we do not';
comment on column clin_health_issue.id_patient is
 	'id of patient this health issue relates to, should
	 be reference but might be outside our own database';
comment on column clin_health_issue.description is
	'descriptive name of this health issue, may
	 change over time as evidence increases';
comment on column clin_health_issue.age_noted is
	'at what age the patient acquired the condition';
comment on column clin_health_issue.is_active is
	'whether this health issue (problem) is active';
comment on column clin_health_issue.clinically_relevant is
	'whether this health issue (problem) has any clinical relevance';

-- ===================================================================
-- episode related tables
create table clin_episode (
	pk serial primary key,
	fk_health_issue integer
		default null
		references clin_health_issue(id)
		on update cascade
		on delete restrict,
	fk_patient integer
		default null
		references xlnk_identity(xfk_identity)
		on update cascade
		on delete restrict,
	description text
		not null
		check (trim(description) != ''),
	is_open boolean
		default true
) inherits (audit_fields);

alter table clin_episode add constraint only_standalone_epi_has_patient
	check (
		((fk_health_issue is null) and (fk_patient is not null))
			or
		((fk_health_issue is not null) and (fk_patient is null))
	);

select add_table_for_audit('clin_episode');

comment on table clin_episode is
	'clinical episodes such as "Otitis media",
	"traffic accident 7/99", "Hepatitis B"';
comment on column clin_episode.fk_health_issue is
	'health issue this episode belongs to';
comment on column clin_episode.fk_patient is
	'patient this episode belongs to,
	 may only be set if fk_health_issue is Null
	 thereby removing redundancy';
comment on column clin_episode.description is
	'description/name of this episode';
comment on column clin_episode.is_open is
	'whether the episode is open (eg. there is activity for it),
	 means open in a temporal sense as in "not closed yet"';

-- -------------------------------------------------------------------
create table last_act_episode (
	id serial primary key,
	fk_episode integer
		unique
		not null
		references clin_episode(pk)
		on update cascade
		on delete cascade,
	id_patient integer
		unique
		not null
		references xlnk_identity(xfk_identity)
		on update cascade
		on delete restrict
);

comment on table last_act_episode is
	'records the most recently active episode per patient,
	 upon instantiation of a patient object it should read
	 the most recently active episode from this table,
	 upon deletion of the object, the last active episode
	 should be recorded here,
	 do *not* rely on the content of this table *during*
	 the life time of a patient object as the value can
	 change from under us';

-- ===================================================================
-- encounter related tables
-- -------------------------------------------------------------------
create table encounter_type (
	pk serial primary key,
	description text
		unique
		not null
);

comment on TABLE encounter_type is
	'these are the types of encounter';

-- -------------------------------------------------------------------
create table clin_encounter (
	id serial primary key,
	fk_patient integer
		not null
		references xlnk_identity(xfk_identity)
		on update cascade
		on delete restrict,
	-- FIXME: probably remove this field ...
	fk_provider integer,
	fk_type integer
		not null
		default 1
		references encounter_type(pk)
		on update cascade
		on delete restrict,
	fk_location integer,
	source_time_zone interval,
	description text
		default null
		check (trim(both from coalesce(description, 'xxxDEFAULTxxx')) != ''),
	started timestamp with time zone
		not null
		default CURRENT_TIMESTAMP,
	last_affirmed timestamp with time zone
		not null
		default CURRENT_TIMESTAMP
) inherits (audit_fields);

-- remote foreign keys
select add_x_db_fk_def('clin_encounter', 'fk_location', 'personalia', 'org', 'id');
select add_x_db_fk_def('clin_encounter', 'fk_provider', 'personalia', 'staff', 'pk');

comment on table clin_encounter is
	'a clinical encounter between a person and the health care system';
comment on COLUMN clin_encounter.fk_patient is
	'PK of subject of care, should be PUPIC, actually';
comment on COLUMN clin_encounter.fk_provider is
	'PK of (main) provider of care';
comment on COLUMN clin_encounter.fk_type is
	'PK of type of this encounter';
comment on COLUMN clin_encounter.fk_location is
	'PK of location *of care*, e.g. where the provider is at';
comment on column clin_encounter.source_time_zone is
	'time zone of location, used to approximate source time
	 zone for all timestamps in this encounter';
comment on column clin_encounter.description is
	'descriptive name of this encounter, may change over time;
	 could be RFE, if "xxxDEFAULTxxx" applications should
	 display "<date> (<provider>): <type>" plus some marker for "default"';

-- -------------------------------------------------------------------
create table curr_encounter (
	id serial primary key,
	fk_encounter integer
		not null
		references clin_encounter(id)
		on update cascade
		on delete cascade,
	started timestamp with time zone
		not null
		default CURRENT_TIMESTAMP,
	last_affirmed timestamp with time zone
		not null
		default CURRENT_TIMESTAMP,
	comment text default 'affirmed'
);

comment on table curr_encounter is
	'currently ongoing encounters are stored in this table,
	 clients are supposed to check this table or create a
	 new encounter if appropriate';
comment on column curr_encounter.last_affirmed is
	'clients are supposed to update this field when appropriate
	 such that the encounter detection heuristics in other clients
	 has something to work with';
comment on column curr_encounter."comment" is
	'clients may save an arbitrary comment here when
	 updating last_affirmed, useful for later perusal';

-- ===================================================================
-- EMR items root with narrative aggregation
-- -------------------------------------------------------------------
create table clin_root_item (
	pk_item serial primary key,
	clin_when timestamp with time zone
		not null
		default CURRENT_TIMESTAMP,
	fk_encounter integer
		not null
		references clin_encounter(id)
		on update cascade
		on delete restrict,
	fk_episode integer
		not null
		references clin_episode(pk)
		on update cascade
		on delete restrict,
	narrative text,
	soap_cat text
		not null
		check(lower(soap_cat) in ('s', 'o', 'a', 'p'))
) inherits (audit_fields);

comment on TABLE clin_root_item is
	'ancestor table for clinical items of any kind, basic
	 unit of clinical information, do *not* store data in
	 here directly, use child tables,
	 contains all the clinical narrative aggregated for full
	 text search, ancestor for all tables that want to store
	 clinical free text';
comment on COLUMN clin_root_item.pk_item is
	'the primary key, not named "id" or "pk" as usual since child
	 tables will have "id"/"pk"-named primary keys already and
	 we would get duplicate columns while inheriting from this
	 table';
comment on column clin_root_item.clin_when is
	'when this clinical item became known, can be different from
	 when it was entered into the system (= audit_fields.modified_when)';
comment on COLUMN clin_root_item.fk_encounter is
	'the encounter this item belongs to';
comment on COLUMN clin_root_item.fk_episode is
	'the episode this item belongs to';
comment on column clin_root_item.narrative is
	'each clinical item by default inherits a free text field for clinical narrative';
comment on column clin_root_item.soap_cat is
	'each clinical item must be in one of the S, O, A, P categories';

-- --------------------------------------------
create table clin_item_type (
	pk serial primary key,
	type text
		default 'history'
		unique
		not null,
	code text
		default 'Hx'
		unique
		not null
) inherits (audit_fields);

select add_table_for_audit('clin_item_type');

comment on table clin_item_type is
	'stores arbitrary types for tagging clinical items';
comment on column clin_item_type.type is
	'the full name of the item type such as "family history"';
comment on column clin_item_type.code is
	'shorthand for the type, eg "FHx"';

-- --------------------------------------------
create table lnk_type2item (
	pk serial primary key,
	fk_type integer
		not null
		references clin_item_type(pk)
		on update cascade
		on delete cascade,
	fk_item integer
		not null
--		references clin_root_item(pk_item)
--		on update cascade
--		on delete cascade
		,
	unique (fk_type, fk_item)
) inherits (audit_fields);

select add_table_for_audit('lnk_type2item');

comment on table lnk_type2item is
	'allow to link many-to-many between clin_root_item and clin_item_type';
-- FIXME: recheck for 8.0
comment on column lnk_type2item.fk_item is
	'the item this type is linked to,
	 since PostgreSQL apparently cannot reference a value
	 inserted from a child table (?) we must simulate
	 referential integrity checks with a custom trigger,
	 this, however, does not deal with update/delete
	 cascading :-(';

-- ============================================
-- specific EMR content tables: SOAP++
-- --------------------------------------------
-- soap cats
create table soap_cat_ranks (
	pk serial primary key,
	rank integer
		not null
		check (rank in (1,2,3,4)),
	soap_cat character(1)
		not null
		check (lower(soap_cat) in ('s', 'o', 'a', 'p'))
);

-- narrative
create table clin_narrative (
	pk serial primary key,
	is_rfe boolean
		not null
		default false,
	is_aoe boolean
		not null
		default false,
	unique(fk_encounter, fk_episode, narrative, soap_cat)
) inherits (clin_root_item);

alter table clin_narrative add foreign key (fk_encounter)
		references clin_encounter(id)
		on update cascade
		on delete restrict;
alter table clin_narrative add foreign key (fk_episode)
		references clin_episode(pk)
		on update cascade
		on delete restrict;
alter table clin_narrative add constraint aoe_xor_rfe
	check (not (is_rfe is true and is_aoe is true));
alter table clin_narrative add constraint rfe_is_subj
	check ((is_rfe is false) or (is_rfe is true and soap_cat='s'));
alter table clin_narrative add constraint aoe_is_assess
	check ((is_aoe is false) or (is_aoe is true and soap_cat='a'));
alter table clin_narrative add constraint narrative_neither_null_nor_empty
	check (trim(coalesce(narrative, '')) != '');

select add_table_for_audit('clin_narrative');

comment on TABLE clin_narrative is
	'Used to store clinical free text *not* associated
	 with any other table. Used to implement a simple
	 SOAP structure. Also other tags can be associated
	 via link tables.';
comment on column clin_narrative.clin_when is
	'when did the item reach clinical reality';
comment on column clin_narrative.is_rfe is
	'if TRUE the narrative stores a Reason for Encounter
	 which also implies soap_cat = s';
comment on column clin_narrative.is_aoe is
	'if TRUE the narrative stores an Assessment of Encounter
	 which also implies soap_cat = a';

-- --------------------------------------------
-- coded narrative
create table coded_narrative (
	pk serial primary key,
	term text
		not null
		check (trim(term) != ''),
	code text
		not null
		check (trim(code) != ''),
	xfk_coding_system text
		not null
		check (trim(code) != ''),
	unique (term, code, xfk_coding_system)
) inherits (audit_fields);

select add_table_for_audit('coded_narrative');
select add_x_db_fk_def('coded_narrative', 'xfk_coding_system', 'reference', 'ref_source', 'name_short');

comment on table coded_narrative is
	'associates codes with text snippets which may be in use in clinical tables';
comment on column coded_narrative.term is
	'the text snippet that is to be coded';
comment on column coded_narrative.code is
	'the code in the coding system';
comment on column coded_narrative.xfk_coding_system is
	'the coding system used to code the text snippet';

--create table lnk_code2narr (
--	pk serial primary key,
--	fk_narrative integer
--		not null
--		references clin_narrative(pk)
--		on update cascade
--		on delete cascade,
--	code text
--		not null,
--	xfk_coding_system text
--		not null,
--	unique (fk_narrative, code, xfk_coding_system)
--) inherits (audit_fields);

--select add_table_for_audit('lnk_code2narr');
--select add_x_db_fk_def('lnk_code2narr', 'xfk_coding_system', 'reference', 'ref_source', 'name_short');

--comment on table lnk_code2narr is
--	'links codes to narrative items';
--comment on column lnk_code2narr.code is
--	'the code in the coding system';
--comment on column lnk_code2narr.xfk_coding_system is
--	'the coding system used to code the narrative item';

-- --------------------------------------------
-- general FH storage
create table hx_family_item (
	pk serial primary key,
	fk_narrative_condition integer
		default null
		references clin_narrative(pk)
		on update cascade
		on delete restrict,
	fk_relative integer
		default null
		references xlnk_identity(xfk_identity)
		on update cascade
		on delete set null,
	name_relative text
		default null
		check (coalesce(trim(name_relative), 'dummy') != ''),
	dob_relative timestamp with time zone
		default null,
	condition text
		default null
		check (coalesce(trim(condition), 'dummy') != ''),
	age_noted text,
	age_of_death interval
		default null,
	is_cause_of_death boolean
		not null
		default false,
	unique (name_relative, dob_relative, condition),
	unique (fk_relative, condition)
) inherits (audit_fields);

select add_table_for_audit('hx_family_item');

alter table hx_family_item add constraint link_or_know_condition
	check (
		(fk_narrative_condition is not null and condition is null)
			or
		(fk_narrative_condition is null and condition is not null)
	);

alter table hx_family_item add constraint link_or_know_relative
	check (
		-- from linked narrative
		(fk_narrative_condition is not null and fk_relative is null and name_relative is null and dob_relative is null)
			or
		-- from linked relative
		(fk_narrative_condition is null and fk_relative is not null and name_relative is null and dob_relative is null)
			or
		-- from name
		(fk_narrative_condition is null and fk_relative is null and name_relative is not null)
	);

comment on table hx_family_item is
	'stores family history items independant of the patient,
	 this is out-of-EMR so that several patients can link to it';
comment on column hx_family_item.fk_narrative_condition is
	'can point to a narrative item of a relative if in database';
comment on column hx_family_item.fk_relative is
	'foreign key to relative if in database';
comment on column hx_family_item.name_relative is
	'name of the relative if not in database';
comment on column hx_family_item.dob_relative is
	'DOB of relative if not in database';
comment on column hx_family_item.condition is
	'narrative holding the condition the relative suffered from,
	 must be NULL if fk_narrative_condition is not';
comment on column hx_family_item.age_noted is
	'at what age the relative acquired the condition';
comment on column hx_family_item.age_of_death is
	'at what age the relative died';
comment on column hx_family_item.is_cause_of_death is
	'whether relative died of this problem, Richard
	 suggested to allow that several times per relative';


-- patient linked FH
create table clin_hx_family (
	pk serial primary key,
	fk_hx_family_item integer
		not null
		references hx_family_item(pk)
		on update cascade
		on delete restrict
) inherits (clin_root_item);

alter table clin_hx_family add foreign key (fk_encounter)
		references clin_encounter(id)
		on update cascade
		on delete restrict;
alter table clin_hx_family add foreign key (fk_episode)
		references clin_episode(pk)
		on update cascade
		on delete restrict;
alter table clin_hx_family add constraint narrative_neither_null_nor_empty
	check (trim(coalesce(narrative, '')) != '');
-- FIXME: constraint trigger has_type(fHx)

select add_table_for_audit('clin_hx_family');

comment on table clin_hx_family is
	'stores family history for a given patient';
comment on column clin_hx_family.clin_when is
	'when the family history item became known';
comment on column clin_hx_family.fk_encounter is
	'encounter during which family history item became known';
comment on column clin_hx_family.fk_episode is
	'episode to which family history item is of importance';
comment on column clin_hx_family.narrative is
	'how is the afflicted person related to the patient';
comment on column clin_hx_family.soap_cat is
	'as usual, must be NULL if fk_narrative_condition is not but
	 this is not enforced and only done in the view';

-- --------------------------------------------
-- patient attached diagnoses
create table clin_diag (
	pk serial primary key,
	fk_narrative integer
		unique
		not null
		references clin_narrative(pk)
		on update cascade
		on delete restrict,
	laterality char
		default null
		check ((laterality in ('l', 'r', 'b', '?')) or (laterality is null)),
	is_chronic boolean
		not null
		default false,
	is_active boolean
		not null
		default true,
	is_definite boolean
		not null
		default false,
	clinically_relevant boolean
		not null
		default true
) inherits (audit_fields);

alter table clin_diag add constraint if_active_then_relevant
	check (
		(is_active = false)
			or
		((is_active = true) and (clinically_relevant = true))
	);
-- not sure about that one:
--alter table clin_diag add constraint if_chronic_then_relevant
--	check (
--		(is_chronic = false)
--			or
--		((is_chronic = true) and (clinically_relevant = true))
--	);

select add_table_for_audit('clin_diag');

comment on table clin_diag is
	'stores additional detail on those clin_narrative
	 rows where soap_cat=a that are true diagnoses,
	 true diagnoses DO have a code from one of the coding systems';
comment on column clin_diag.is_chronic is
	'whether this diagnosis is chronic, eg. no complete
	 cure is to be expected, regardless of whether it is
	 *active* right now (think of active/non-active phases
	 of Multiple Sclerosis which is sure chronic)';
comment on column clin_diag.is_active is
	'whether diagnosis is currently active or dormant';
comment on column clin_diag.clinically_relevant is
	'whether this diagnosis is considered clinically
	 relevant, eg. significant;
	 currently active diagnoses are considered to
	 always be relevant, while inactive ones may
	 or may not be';
-- --------------------------------------------
create table clin_aux_note (
	pk serial primary key
) inherits (clin_root_item);

alter table clin_aux_note add foreign key (fk_encounter)
		references clin_encounter(id)
		on update cascade
		on delete restrict;
alter table clin_aux_note add foreign key (fk_episode)
		references clin_episode(pk)
		on update cascade
		on delete restrict;

select add_table_for_audit('clin_aux_note');

comment on TABLE clin_aux_note is
	'Other tables link to this if they need more free text fields.';

-- ============================================
-- vaccination tables
-- ============================================
create table vacc_indication (
	id serial primary key,
	description text unique not null
) inherits (audit_fields);

select add_table_for_audit('vacc_indication');
select add_table_for_scoring('vacc_indication');

comment on table vacc_indication is
	'definition of indications for vaccinations';
comment on column vacc_indication.description is
	'description of indication, eg "Measles"';

-- --------------------------------------------
create table lnk_vacc_ind2code (
	id serial primary key,
	fk_indication integer
		not null
		references vacc_indication(id)
		on delete cascade
		on update cascade,
	code text not null,
	coding_system text not null,
	unique (fk_indication, code, coding_system)
);

-- remote foreign keys
select add_x_db_fk_def('lnk_vacc_ind2code', 'coding_system', 'reference', 'ref_source', 'name_short');

comment on table lnk_vacc_ind2code is
	'links vaccination indications to disease codes,
	 useful for cross-checking whether a patient
	 should be considered immune against a disease,
	 multiple codes from multiple coding systems can
	 be linked against one vaccination indication';

-- --------------------------------------------
create table vacc_route (
	id serial primary key,
	abbreviation text unique not null,
	description text unique not null
) inherits (audit_fields);

select add_table_for_audit('vacc_route');

comment on table vacc_route is
	'definition of route via which vaccine is given,
	 currently i.m. and p.o. only but may include
	 "via genetically engineered food" etc in the
	 future';

-- --------------------------------------------
-- maybe this table belongs into "service"
-- "inventory"/"stock" or something one day
create table vaccine (
	id serial primary key,
	id_route integer
		not null
		references vacc_route(id)
		default 1,
	trade_name text unique not null,
	short_name text not null,
	is_live boolean not null default false,
	min_age interval
		not null
		check(min_age > interval '0 seconds'),
	max_age interval
		default null
		check((max_age is null) or (max_age >= min_age)),
	last_batch_no text default null,
	comment text,
	unique (trade_name, short_name)
) inherits (audit_fields);

select add_table_for_audit('vaccine');

comment on table vaccine is
	'definition of a vaccine as available on the market';
comment on column vaccine.id_route is
	'route this vaccine is given';
comment on column vaccine.trade_name is
	'full name the vaccine is traded under';
comment on column vaccine.short_name is
	'common, maybe practice-specific shorthand name
	 for referring to this vaccine';
comment on column vaccine.is_live is
	'whether this is a live vaccine';
comment on column vaccine.min_age is
	'minimum age this vaccine is licensed for';
comment on column vaccine.max_age is
	'maximum age this vaccine is licensed for';
comment on column vaccine.last_batch_no is
	'serial # of most recently used batch, for
	 rapid data input purposes';

-- --------------------------------------------
create table lnk_vaccine2inds (
	id serial primary key,
	fk_vaccine integer
		not null
		references vaccine(id)
		on delete cascade
		on update cascade,
	fk_indication integer
		not null
		references vacc_indication(id)
		on delete cascade
		on update cascade,
	unique (fk_vaccine, fk_indication)
);

comment on table lnk_vaccine2inds is
	'links vaccines to their indications';

-- --------------------------------------------
create table vacc_regime (
	id serial primary key,
	name text unique not null,
	fk_recommended_by integer,
	fk_indication integer
		not null
		references vacc_indication(id)
		on update cascade
		on delete restrict,
	comment text,
	unique(fk_recommended_by, fk_indication, name)
) inherits (audit_fields);

select add_table_for_audit('vacc_regime');

-- remote foreign keys:
select add_x_db_fk_def('vacc_regime', 'fk_recommended_by', 'reference', 'ref_source', 'pk');

comment on table vacc_regime is
	'holds vaccination schedules/regimes/target diseases';
comment on column vacc_regime.fk_recommended_by is
	'organization recommending this vaccination';
comment on column vacc_regime.fk_indication is
	'vaccination indication this regime is targeted at';
comment on column vacc_regime.name is
	'regime name: schedule/disease/target bacterium...';

-- --------------------------------------------
create table lnk_pat2vacc_reg (
	pk serial primary key,
	fk_patient integer
		not null
		references xlnk_identity(xfk_identity)
		on update cascade
		on delete cascade,
	fk_regime integer
		not null
		references vacc_regime(id)
		on update cascade
		on delete restrict,
	unique(fk_patient, fk_regime)
) inherits (audit_fields);

select add_table_for_audit('lnk_pat2vacc_reg');
-- select add_table_for_notifies('lnk_pat2vacc_reg', 'vacc');

comment on table lnk_pat2vacc_reg is
	'links patients to vaccination regimes they are actually on,
	 this allows for per-patient selection of regimes to be
	 followed, eg. children at different ages may be on different
	 vaccination schedules or some people are on a schedule due
	 to a trip abroad while most others are not';

-- --------------------------------------------
create table vacc_def (
	id serial primary key,
	fk_regime integer
		not null
		references vacc_regime(id)
		on delete cascade
		on update cascade,
	is_booster boolean
		default false
		check (((is_booster is true) and (seq_no is null)) or ((is_booster is false) and (seq_no > 0))),
	seq_no integer
		default null
		check (((is_booster is true) and (seq_no is null)) or ((is_booster is false) and (seq_no > 0))),
	min_age_due interval
		not null
		check (min_age_due > '0 seconds'::interval),
	max_age_due interval
		default null
		check ((max_age_due is null) or (max_age_due >= min_age_due)),
	min_interval interval
		default null
		check (
			((is_booster=true) and (min_interval is not null) and (min_interval > '0 seconds'::interval))
				or
			((seq_no = 1) and (min_interval is null))
				or
			((seq_no > 1) and (min_interval is not null) and (min_interval > '0 seconds'::interval))
		),
	comment text,
	unique(fk_regime, seq_no)
) inherits (audit_fields);

select add_table_for_audit('vacc_def');

comment on table vacc_def is
	'defines a given vaccination event for a particular regime';
comment on column vacc_def.fk_regime is
	'regime to which this event belongs';
comment on column vacc_def.is_booster is
	'does this definition represent a booster';
comment on column vacc_def.seq_no is
	'sequence number for this vaccination event
	 within a particular schedule/regime,
	 NULL if (is_booster == true)';
comment on column vacc_def.min_age_due is
	'minimum age at which this shot is due';
comment on column vacc_def.max_age_due is
	'maximum age at which this shot is due,
	 if max_age_due = NULL: no maximum age';
comment on column vacc_def.min_interval is
	'if (is_booster == true):
		recommended interval for boostering
	 id (is_booster == false):
	 	minimum interval after previous vaccination,
		NULL if seq_no == 1';

-- --------------------------------------------
create table vaccination (
	id serial primary key,
	-- isn't this redundant ?
	fk_patient integer
		not null
		references xlnk_identity(xfk_identity)
		on update cascade
		on delete restrict,
	fk_provider integer
		not null,
	fk_vaccine integer
		not null
		references vaccine(id)
		on delete restrict
		on update cascade,
	site text
		default 'not recorded',
	batch_no text
		not null
		default 'not recorded',
	unique (fk_patient, fk_vaccine, clin_when)
) inherits (clin_root_item);
-- Richard tells us that "refused" should go into progress note

alter table vaccination add foreign key (fk_encounter)
		references clin_encounter(id)
		on update cascade
		on delete restrict;
alter table vaccination add foreign key (fk_episode)
		references clin_episode(pk)
		on update cascade
		on delete restrict;
alter table vaccination alter column soap_cat set default 'p';

select add_table_for_audit('vaccination');
select add_table_for_notifies('vaccination', 'vacc');

select add_x_db_fk_def('vaccination', 'fk_provider', 'personalia', 'staff', 'pk');

comment on table vaccination is
	'holds vaccinations actually given';

-- --------------------------------------------
-- this table will be even larger than vaccination ...
--create table lnk_vacc2vacc_def (
--	pk serial primary key,
--	fk_vaccination integer
--		not null
--		references vaccination(id)
--		on delete cascade
--		on update cascade,
--	fk_vacc_def integer
--		not null
--		references vacc_def(id)
--		on delete restrict
--		on update cascade,
--	unique (fk_vaccination, fk_vacc_def)
--) inherits (audit_fields);

--comment on column lnk_vacc2vacc_def.fk_vacc_def is
--	'the vaccination event a particular
--	 vaccination is supposed to cover, allows to
--	 link out-of-band vaccinations into regimes,
--	 not currently used';

-- ============================================
-- allergies tables
create table allergy_state (
	id serial primary key,
	fk_patient integer
		unique
		not null
		references xlnk_identity(xfk_identity)
		on update cascade
		on delete restrict,
	has_allergy integer
		default null
		check (has_allergy in (null, -1, 0, 1))
) inherits (audit_fields);

select add_table_for_audit('allergy_state');

comment on column allergy_state.has_allergy is
	'patient allergenic state:
	 - null: unknown, not asked, no data available
	 - -1: unknown, asked, no data obtained
	 - 0:  known, asked, has no known allergies
	 - 1:  known, asked, does have allergies
	';

-- --------------------------------------------
create table _enum_allergy_type (
	id serial primary key,
	value text unique not null
);

-- --------------------------------------------
create table allergy (
	id serial primary key,
	substance text not null,
	substance_code text default null,
	generics text default null,
	allergene text default null,
	atc_code text default null,
	id_type integer
		not null
		references _enum_allergy_type(id),
	generic_specific boolean default false,
	definite boolean default false
) inherits (clin_root_item);

-- narrative provided by clin_root_item

alter table allergy add foreign key (fk_encounter)
		references clin_encounter(id)
		on update cascade
		on delete restrict;
alter table allergy add foreign key (fk_episode)
		references clin_episode(pk)
		on update cascade
		on delete restrict;
alter table allergy alter column soap_cat set default 'o';

select add_table_for_audit('allergy');
select add_table_for_notifies('allergy', 'allg');

comment on table allergy is
	'patient allergy details';
comment on column allergy.substance is
	'real-world name of substance the patient reacted to, brand name if drug';
comment on column allergy.substance_code is
	'data source specific opaque product code; must provide a link
	 to a unique product/substance in the database in use; should follow
	 the parseable convention of "<source>::<source version>::<identifier>",
	 e.g. "MIMS::2003-1::190" for Zantac; it is left as an exercise to the
	 application to know what to do with this information';
comment on column allergy.generics is
	'names of generic compounds if drug; brand names change/disappear, generic names do not';
comment on column allergy.allergene is
	'name of allergenic ingredient in substance if known';
comment on column allergy.atc_code is
	'ATC code of allergene or substance if approprate, applicable for penicilline, not so for cat fur';
comment on column allergy.id_type is
	'allergy/sensitivity';
comment on column allergy.generic_specific is
	'only meaningful for *drug*/*generic* reactions:
	 1) true: applies to one in "generics" forming "substance",
			  if more than one generic listed in "generics" then
			  "allergene" *must* contain the generic in question;
	 2) false: applies to drug class of "substance";';
comment on column allergy.definite is
	'true: definite, false: not definite';
comment on column allergy.narrative is
	'used as field "reaction"';

-- ============================================
-- form instance tables
-- --------------------------------------------
create table form_instances (
	pk serial primary key,
	fk_form_def integer
		not null
		references form_defs(pk)
		on update cascade
		on delete restrict,
	form_name text not null
) inherits (clin_root_item);

alter table form_instances add foreign key (fk_encounter)
		references clin_encounter(id)
		on update cascade
		on delete restrict;
alter table form_instances add foreign key (fk_episode)
		references clin_episode(pk)
		on update cascade
		on delete restrict;
alter table form_instances add constraint form_is_plan
	check (soap_cat='p');

--select add_x_db_fk_def('form_instances', 'xfk_form_def', 'reference', 'form_defss', 'pk');

select add_table_for_audit('form_instances');

comment on table form_instances is
	'instances of forms, like a log of all processed forms';
comment on column form_instances.fk_form_def is
	'points to the definition of this instance,
	 this FK will fail once we start separating services,
	 make it into a x_db_fk then';
comment on column form_instances.form_name is
	'a string uniquely identifying the form template,
	 necessary for the audit trail';
comment on column form_instances.narrative is
	'can be used as a status field, eg. "printed", "faxed" etc.';

-- --------------------------------------------
create table form_data (
	pk serial primary key,
	fk_instance integer
		not null
		references form_instances(pk)
		on update cascade
		on delete restrict,
	fk_form_field integer
		not null
		references form_fields(pk)
		on update cascade
		on delete restrict,
	value text not null,
	unique(fk_instance, fk_form_field)
) inherits (audit_fields);

--select add_x_db_fk_def('form_data', 'xfk_form_field', 'reference', 'form_fields', 'pk');

select add_table_for_audit('form_data');

comment on table form_data is
	'holds the values used in form instances, for
	 later re-use/validation';
comment on column form_data.fk_instance is
	'the form instance this value was used in';
comment on column form_data.fk_form_field is
	'points to the definition of the field in the form
	 which in turn defines the place holder in the
	 template to replace with <value>';
comment on column form_data.value is
	'the value to replace the place holder with';

-- ============================================
-- medication tables
create table clin_medication (
	pk serial primary key,
	-- administrative
	last_prescribed date
		not null
		default CURRENT_DATE,
	fk_last_script integer
		default null
		references form_instances(pk)
		on update cascade
		on delete set null,
	discontinued date
		default null,
	-- identification
	brandname text
		default null,
	generic text
		default null,
	adjuvant text,
	dosage_form text
		not null, --check (form in ('spray', 'cap', 'tab', 'inh', 'neb', 'cream', 'syrup', 'lotion', 'drop', 'inj', 'oral liquid'))
	ufk_drug text
		not null,
	drug_db text
		not null,
	atc_code text
		not null,
	is_CR boolean
		not null,
	-- medical application
	dosage numeric[]
		not null,
	period interval
		not null,
	dosage_unit text
		not null
		check (dosage_unit in ('g', 'each', 'ml')),
	directions text
		default null,
	is_prn boolean
		default false
) inherits (clin_root_item);

alter table clin_medication add foreign key (fk_encounter)
		references clin_encounter(id)
		on update cascade
		on delete restrict;
alter table clin_medication add foreign key (fk_episode)
		references clin_episode(pk)
		on update cascade
		on delete restrict;
alter table clin_medication add constraint medication_is_plan
	check (soap_cat='p');
alter table clin_medication add constraint brand_or_generic_required
	check ((brandname is not null) or (generic is not null));
alter table clin_medication add constraint prescribed_after_started
	check (last_prescribed >= clin_when::date);
alter table clin_medication add constraint discontinued_after_prescribed
	check (discontinued >= last_prescribed);

select add_table_for_audit ('clin_medication');

comment on table clin_medication is
	'Representing what the patient is taking *now*, eg. a medication
	 status (similar to vaccination status). Not a log of prescriptions.
	 If drug was prescribed by brandname it may span several (unnamed
	 or listed) generics. If generic substances were prescribed there
	 would be one row per substance in this table.

	- forms engine will record each script and its fields
	- audit mechanism will record all changes to this table

Note the multiple redundancy of the stored drug data.
Applications should try in this order:
- internal database code
- brandname
- ATC code
- generic name(s) (in constituents)
';
comment on column clin_medication.clin_when is
	'used as "started" column
	 - when did patient start to take this medication
	 - in many cases date of first prescription - but not always
	 - for newly prescribed drugs identical to last_prescribed';
comment on column clin_medication.narrative is
	'used as "prescribed_for" column
	 - use to specify intent beyond treating issue at hand';
comment on column clin_medication.last_prescribed is
	'date last script written for this medication';
comment on column clin_medication.fk_last_script is
	'link to the most recent script by which this drug
	 was prescribed';
comment on column clin_medication.discontinued is
	'date at which medication was *discontinued*,
	 note that the date when a script *expires*
	 should be calculatable';
comment on column clin_medication.brandname is
	'the brand name of this drug under which it is
	 marketed by the manufacturer';
comment on column clin_medication.generic is
	'the generic name of the active substance';
comment on column clin_medication.adjuvant is
	'free text describing adjuvants, such as "orange-flavoured" etc.';
comment on column clin_medication.dosage_form is
	'the form the drug is delivered in, eg liquid, cream, table, etc.';
comment on column clin_medication.ufk_drug is
	'the identifier for this drug in the source database,
	 may or may not be an opaque value as regards GnuMed';
comment on column clin_medication.drug_db is
	'the drug database used to populate this entry';
comment on column clin_medication.atc_code is
	'the Anatomic Therapeutic Chemical code for this drug,
	 used to compute possible substitutes';
comment on column clin_medication.is_CR is
	'Controlled Release. Some drugs are marketed under the
	 same name although one is slow release while the other
	 is normal release.';
comment on column clin_medication.dosage is
	'an array of doses describing how the drug is taken
	 over the dosing cycle, for example:
	  - 2 mane 2.5 nocte would be [2, 2.5], period="24 hours"
	  - 2 one and 2.5 the next would be [2, 2.5], period="2 days"
	  - once a week would be [1] with period="1 week"';
comment on column clin_medication.period is
	'the length of the dosing cycle, in hours';
comment on column clin_medication.dosage_unit is
	'the unit the dosages are measured in,
	 "each" for discrete objects like tablets';
comment on column clin_medication.directions is
	'free text for patient/pharmacist directions,
	 such as "with food" etc';
comment on column clin_medication.is_prn is
	'true if "pro re nata" (= as required)';

-- ===================================================================
-- following tables not yet converted to EMR structure ...
-- -------------------------------------------------------------------

create table enum_confidentiality_level (
	id SERIAL primary key,
	description text
);

comment on table enum_confidentiality_level is
	'Various levels of confidentialoty of a coded diagnosis, such as public, clinical staff, treating doctor, etc.';

-- ============================================
-- Drug related tables



-- --------------------------------------------
-- IMHO this does not belong in here
create table constituent
(
	genericname text not null,
	amount float not null,
	amount_unit text not null check (amount_unit in 
				('g', 'ml', 'mg', 'mcg', 'IU')),
	id_drug integer not null references clin_medication (pk),
	unique (genericname, id_drug)
);

comment on table constituent is
'the constituent substances of the various drugs (normalised out to support compound drugs like Augmentin)';
comment on column constituent.genericname is
'the English IUPHARM standard name, as a base, with no adjuvant, in capitals. So MORPHINE. not Morphine, not MORPHINE SULPHATE, not MORPHINIUM';
comment on column constituent.amount is
'the amount of drug (if salt, the amount of active base substance, in a unit (see amount_unit above)';

-- =============================================
create table referral (
	id serial primary key,
	fk_referee integer
		not null
		references xlnk_identity(xfk_identity)
		on update cascade
		on delete restrict,
	fk_form integer
		not null
		references form_instances (pk) 
) inherits (clin_root_item);

alter table referral add foreign key (fk_encounter)
		references clin_encounter(id)
		on update cascade
		on delete restrict;
alter table referral add foreign key (fk_episode)
		references clin_episode(pk)
		on update cascade
		on delete restrict;

select add_table_for_audit ('referral');

comment on table referral is 'table for referrals to defined individuals';
comment on column referral.fk_referee is 'person to whom the referral is directed';
comment on column referral.narrative is
	'inherited from clin_root_item;
	 stores text of referral letter';
comment on column referral.fk_form is 'foreign key to the form instance of
this referral.';

-- =============================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename='$RCSfile: gmclinical.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmclinical.sql,v $', '$Revision: 1.160 $');

-- =============================================
-- $Log: gmclinical.sql,v $
-- Revision 1.160  2005-06-19 13:33:51  ncq
-- - manually inherit foreign keys into clin_root_item children
--
-- Revision 1.159  2005/04/17 16:40:36  ncq
-- - after more discussion on the list realize that clin_health_issue
--   is pretty much the same as past_history, hence add the sensible
--   fields from Richard's experience
--
-- Revision 1.158  2005/04/08 10:00:46  ncq
-- - cleanup
-- - remove lnk_code2narr, add coded_narrative instead
--
-- Revision 1.157  2005/03/31 20:10:47  ncq
-- - missing () in check constraint
--
-- Revision 1.156  2005/03/31 17:52:18  ncq
-- - cleanup
-- - add on update/delete
-- - improve check constraint
-- - add soap_cat_ranks
--
-- Revision 1.155  2005/03/21 20:10:56  ncq
-- - improved family history tables, getting close now
--
-- Revision 1.154  2005/03/20 18:10:00  ncq
-- - vastly improve clin_hx_family
-- - add source_timezone to clin_encounter
--
-- Revision 1.153  2005/03/14 14:42:00  ncq
-- - simplified episode naming
-- - add clin_hx_family but not entirely happy with it yet
--
-- Revision 1.152  2005/03/01 20:38:19  ncq
-- - varchar -> text
--
-- Revision 1.151  2005/02/21 18:36:31  ncq
-- - in clin_narrative include fk_episode in unique constraint on field narrative
--
-- Revision 1.150  2005/02/13 14:46:12  ncq
-- - make clin_root_item.soap_cat not null
--
-- Revision 1.149  2005/02/12 13:49:14  ncq
-- - identity.id -> identity.pk
-- - allow NULL for identity.fk_marital_status
-- - subsequent schema changes
--
-- Revision 1.148  2005/02/08 07:20:20  ncq
-- - clin_root_item.narrative, not .comment
--
-- Revision 1.147  2005/02/08 07:07:40  ncq
-- - improve path results staging table
-- - cleanup
--
-- Revision 1.146  2005/01/31 06:22:50  ncq
-- - renamed constraint to better reflect it's implications
--
-- Revision 1.145  2005/01/29 18:42:50  ncq
-- - add form_data.fk_form_field
-- - improve comments on form_instances
--
-- Revision 1.144  2005/01/24 17:57:43  ncq
-- - cleanup
-- - Ian's enhancements to address and forms tables
--
-- Revision 1.143  2004/12/18 09:56:02  ncq
-- - cleanup
-- - id -> pk fix
--
-- Revision 1.142  2004/12/06 21:10:16  ncq
-- - cleanup
--
-- Revision 1.141  2004/11/28 14:35:03  ncq
-- - I first thought putting is_episode_name into clin_narrative would solve
--   more issues that putting fk_clin_narrative into clin_episode, it turned
--   out to be the other way round, however
-- - still missing:
--   - trigger to ensure cyclic consistency between clin_narrative
--     and clin_episode
--   - a (deferred) constraint forcing standalon episodes to have a narrative FK
--
-- Revision 1.140  2004/11/24 15:39:33  ncq
-- - clin_episode does not have clinically_relevant anymore as per discussion on list
--
-- Revision 1.139  2004/11/21 21:54:30  ncq
-- - do not defer initially fk_encounter in clin_root_item
--
-- Revision 1.138  2004/11/21 21:01:08  ncq
-- - clin_episode.is_active -> clin_episode.is_open as per discussion on the list
-- - make clin_root_item.fk_encounter deferrable and initially deferred
--
-- Revision 1.137  2004/11/16 18:59:15  ncq
-- - as per recent discussion re episode/issue naming remove
--   clin_episode.description and add clin_narrative.is_episode_name
--
-- Revision 1.136  2004/11/14 17:55:15  ncq
-- - update clin_encounter.description comment as per Jim's suggestion
--
-- Revision 1.135  2004/10/22 06:53:15  ncq
-- - missing ) prevented this from being bootstrapped, fixed
--
-- Revision 1.134  2004/10/20 21:41:03  ncq
-- - issue/episode must have non-empty name
--
-- Revision 1.133  2004/10/20 13:52:27  sjtan
--
-- placement of , with recent change to field.
--
-- Revision 1.132  2004/10/20 13:16:03  ncq
-- - is_SR -> is_CR
-- - improved comments on clin_medication
--
-- Revision 1.131  2004/10/17 16:27:15  ncq
-- - val_num: float -> numeric + fix views
-- - clin_when::date in prescribed_after_started constraint
--
-- Revision 1.130  2004/10/14 14:56:43  ncq
-- - work on clin_medication to reflect recent discussion
--
-- Revision 1.129  2004/09/25 13:25:56  ncq
-- - is_significant -> clinically_relevant
--
-- Revision 1.128  2004/09/20 23:46:37  ncq
-- - as Syan noted the unique() constraints on clin_episode were plain wrong
--
-- Revision 1.127  2004/09/20 21:14:11  ncq
-- - remove cruft, fix grants
-- - retire lnk_vacc2vacc_def for now as we seem to not need it
--
-- Revision 1.126  2004/09/19 17:16:28  ncq
-- - alter table <> add constraint <> needs table name
--
-- Revision 1.125  2004/09/19 11:25:34  ncq
-- - improved comments
-- - loosened constraints on clin_diag, as found necessary by Jim
--
-- Revision 1.124  2004/09/18 00:20:57  ncq
-- - add active/significant fields to episode/issue table
-- - improve comments
-- - tighten constraints on clin_episode
--
-- Revision 1.123  2004/09/17 21:02:04  ncq
-- - further tighten clin_episode
--
-- Revision 1.122  2004/09/17 20:14:06  ncq
-- - curr_medication -> clin_medication + propagate
-- - partial index on clin_episode.fk_health_issue where fk_health_issue not null
-- - index on clin_medication.discontinued where discontinued not null
-- - rework v_pat_episodes since episode can now have fk_health_issue = null
-- - add val_target_* to v_test_results
-- - fix grants
-- - improve clin_health_issue datatypes + comments
-- - clin_episode: add fk_patient, fk_health_issue nullable
-- - but constrain: if fk_health_issue null then fk_patient NOT none or vice versa
-- - form_instances are soaP
-- - start rework of clin_medication (was curr_medication)
--
-- Revision 1.121  2004/09/03 08:59:18  ncq
-- - improved comments
--
-- Revision 1.120  2004/08/18 08:33:54  ncq
-- - currently, our notify trigger generator can only deal with clin_root_item children
--
-- Revision 1.119  2004/08/16 19:26:45  ncq
-- - add lnk_pat2vacc_reg so we can actually define which
--   patient is on which vaccination schedule
--
-- Revision 1.118  2004/08/04 10:06:49  ncq
-- - typo
--
-- Revision 1.117  2004/07/18 11:50:20  ncq
-- - added arbitrary typing of clin_root_items
--
-- Revision 1.116  2004/07/12 17:23:09  ncq
-- - allow for coding any SOAP row
-- - adjust views/tables to that
--
-- Revision 1.115  2004/07/05 18:13:22  ncq
-- - fold tables into clin_narrative
--
-- Revision 1.114  2004/07/02 15:00:10  ncq
-- - bring rfe/aoe/diag/coded_diag tables/views up to snuff and use them
--
-- Revision 1.113  2004/07/02 00:28:53  ncq
-- - clin_working_diag -> clin_coded_diag + index fixes therof
-- - v_pat_diag rewritten for clin_coded_diag, more useful now
-- - v_patient_items.id_item -> pk_item
-- - grants fixed
-- - clin_rfe/aoe folded into clin_narrative, that enhanced by
--   is_rfe/aoe with appropriate check constraint logic
-- - test data adapted to schema changes
--
-- Revision 1.112  2004/06/30 15:43:52  ncq
-- - clin_note -> clin_narrative
-- - remove v_i18n_curr_encounter
-- - add clin_rfe, clin_aoe
--
-- Revision 1.111  2004/06/26 23:45:50  ncq
-- - cleanup, id_* -> fk/pk_*
--
-- Revision 1.110  2004/06/26 07:33:55  ncq
-- - id_episode -> fk/pk_episode
--
-- Revision 1.109  2004/05/30 21:02:14  ncq
-- - some soap_cat defaults
-- - encounter_type.id -> encounter_type.pk
--
-- Revision 1.108  2004/05/22 11:54:18  ncq
-- - cleanup signal handling on allergy table
--
-- Revision 1.107  2004/05/08 17:37:08  ncq
-- - *_encounter_type -> encounter_type
--
-- Revision 1.106  2004/05/02 19:24:02  ncq
-- - clin_working_diag.narrative is used as the diag name now
-- - a link to clin_aux_note now allows storage of aux note
-- - fix check constraints in clin_working_diag
--
-- Revision 1.105  2004/04/30 12:22:31  ihaywood
-- new referral table
-- some changes to old medications tables, but still need more work
--
-- Revision 1.104  2004/04/30 09:12:30  ncq
-- - fk description clin_working_diag -> clin_aux_note
-- - v_pat_diag
--
-- Revision 1.103  2004/04/29 14:12:50  ncq
-- - add description to clin_working_diag and change meaning of clin_working_diag.narrative
-- - TODO: add trigger to attach clin_aux_note to description field
--
-- Revision 1.102  2004/04/29 13:17:48  ncq
-- - clin_diag -> clin_working_diag
-- - add laterality as per Ian's suggestion
--
-- Revision 1.101  2004/04/27 15:18:38  ncq
-- - rework diagnosis tables + grants for them
--
-- Revision 1.100  2004/04/24 12:59:17  ncq
-- - all shiny and new, vastly improved vaccinations
--   handling via clinical item objects
-- - mainly thanks to Carlos Moro
--
-- Revision 1.99  2004/04/22 13:15:45  ncq
-- - fk update/delete actions on form_instances.fk_form_def
--
-- Revision 1.98  2004/04/21 20:36:07  ncq
-- - cleanup/comments on referral
-- - don't inherit audit_fields in vaccination, those fields are pulled in
--   via clin_root_item already
--
-- Revision 1.97  2004/04/21 15:35:23  ihaywood
-- new referral table (do we still need gmclinical.form_data then?)
--
-- Revision 1.96  2004/04/20 00:17:56  ncq
-- - allergies API revamped, kudos to Carlos
--
-- Revision 1.95  2004/04/14 20:03:59  ncq
-- - fix check constraints on intervals
--
-- Revision 1.94  2004/04/12 22:49:41  ncq
-- - comments
--
-- Revision 1.93  2004/04/11 10:08:36  ncq
-- - tighten check constraints on intervals
--
-- Revision 1.92  2004/04/07 18:16:06  ncq
-- - move grants into re-runnable scripts
-- - update *.conf accordingly
--
-- Revision 1.91  2004/03/19 10:55:40  ncq
-- - remove allergy.reaction -> use clin_root_item.narrative instead
--
-- Revision 1.90  2004/03/18 10:57:20  ncq
-- - several fixes to the data
-- - better constraints on vacc.seq_no/is_booster
--
-- Revision 1.89  2004/03/10 15:45:12  ncq
-- - grants on form tables
--
-- Revision 1.88  2004/03/10 00:05:31  ncq
-- - remove form_status
-- - add form_instance.form_name
--
-- Revision 1.87  2004/03/08 17:03:02  ncq
-- - added form handling tables
--
-- Revision 1.86  2004/02/18 15:28:26  ncq
-- - merge curr_encounter into clin_encounter
--
-- Revision 1.85  2004/01/18 21:56:38  ncq
-- - v_patient_vacc4ind
-- - reformatting DDLs
--
-- Revision 1.84  2004/01/15 15:09:24  ncq
-- - use xlnk_identity extensively
--
-- Revision 1.83  2004/01/15 14:26:25  ncq
-- - add xlnk_identity: this is the only place with an unresolved remote foreign key
-- - make other tables point to this table
--
-- Revision 1.82  2004/01/12 13:16:22  ncq
-- - make vaccine unique on short/long name not short name alone
--
-- Revision 1.81  2004/01/10 01:43:34  ncq
-- - add grants
--
-- Revision 1.80  2004/01/06 23:44:40  ncq
-- - __default__ -> xxxDEFAULTxxx
--
-- Revision 1.79  2004/01/05 00:48:02  ncq
-- - clin_encounter.comment now text instead of varchar
--
-- Revision 1.78  2003/12/29 15:48:27  uid66147
-- - now that we have staff tables use them
-- - factor out vaccination.fk_vacc_def into lnk_vacc2vacc_def
--   since a vaccination can cover several vacc_defs
--
-- Revision 1.77  2003/12/02 00:06:54  ncq
-- - add on update/delete actions on vacc* tables
--
-- Revision 1.76  2003/12/01 22:13:19  ncq
-- - default null on max_age_due
--
-- Revision 1.75  2003/11/28 10:08:38  ncq
-- - fix typos
--
-- Revision 1.74  2003/11/28 01:03:21  ncq
-- - allow null in vacc_def.max_age_due so we can coalesce() in views
--
-- Revision 1.73  2003/11/26 23:20:43  ncq
-- - no need for lnk_vacc_def2regime anymore
--
-- Revision 1.72  2003/11/22 16:52:01  ncq
-- - missing ON in grants
--
-- Revision 1.71  2003/11/22 15:36:47  ncq
-- - fix name clin history editarea id seq
--
-- Revision 1.70  2003/11/17 20:14:45  ncq
-- - cleanup grants, make primary key serial data type
--
-- Revision 1.69  2003/11/17 11:14:53  sjtan
--
-- (perhaps temporary) extra referencing table for past history.
--
-- Revision 1.68  2003/11/16 19:32:17  ncq
-- - clin_when in clin_root_item
--
-- Revision 1.67  2003/11/13 09:45:54  ncq
-- - add clin_date, clin_time to clin_root_item
--
-- Revision 1.66  2003/11/04 00:23:58  ncq
-- - some grants
--
-- Revision 1.65  2003/10/31 23:29:38  ncq
-- - cleanup, id_ -> fk_
--
-- Revision 1.64  2003/10/26 09:41:03  ncq
-- - truncate -> delete from
--
-- Revision 1.63  2003/10/20 22:01:01  ncq
-- - removed use of array type in FKs as per Syan's suggestion
--
-- Revision 1.62  2003/10/19 15:43:00  ncq
-- - even better vaccination tables
--
-- Revision 1.61  2003/10/07 22:29:10  ncq
-- - better comments on vacc_*
--
-- Revision 1.60  2003/10/01 15:44:24  ncq
-- - add vaccination tables, use auditing record table
--
-- Revision 1.59  2003/08/27 00:35:32  ncq
-- - add vaccination tables
--
-- Revision 1.58  2003/08/17 00:25:38  ncq
-- - remove log_ tables, they are now auto-created
--
-- Revision 1.57  2003/08/13 14:30:29  ncq
-- - drugchart -> curr_medication
-- - cleanup
--
-- Revision 1.56  2003/08/10 07:43:11  ihaywood
-- new drug tables
--
-- Revision 1.55  2003/07/27 22:01:05  ncq
-- - coding_systems moved to gmReference
-- - start work on clin_diagnosis, drug* tables pending
--
-- Revision 1.54  2003/06/29 15:25:30  ncq
-- - adapt to audit_fields split-off
-- - make clin_root_item inherit audit_fields but NOT audit_mark, hehe
--
-- Revision 1.53  2003/06/23 21:56:52  ncq
-- - grants on curr_encounter
--
-- Revision 1.52  2003/06/22 16:22:37  ncq
-- - add curr_encounter for tracking active encounters
-- - split clin_aux_note from clin_note so we can cleanly separate
--   deliberate free text from referenced free text (when building EHR
--   views, that is)
-- - grants
--
-- Revision 1.51  2003/06/03 13:49:50  ncq
-- - last_active_episode -> last_act_episode + grants on it
--
-- Revision 1.50  2003/06/02 21:03:41  ncq
-- - last_active_episode: unique on id_patient, not composite(patient/episode)
--
-- Revision 1.49  2003/06/01 11:38:12  ncq
-- - fix spelling of definate -> definite
--
-- Revision 1.48  2003/06/01 10:07:32  sjtan
--
-- change?
--
-- Revision 1.47  2003/05/22 12:56:12  ncq
-- - add "last_active_episode"
-- - adapt to audit_log -> audit_trail
--
-- Revision 1.46  2003/05/14 22:06:27  ncq
-- - merge clin_narrative and clin_item
-- - clin_item -> clin_root_item, general cleanup
-- - set up a few more audits
-- - set up dummy tables for audit trail table inheritance
-- - appropriate grants
--
-- Revision 1.45  2003/05/13 14:49:10  ncq
-- - warning on clin_narrative to not use directly
-- - make allergy the only audited table for now, add audit table for it
--
-- Revision 1.44  2003/05/12 19:29:45  ncq
-- - first stab at real auditing
--
-- Revision 1.43  2003/05/12 12:43:39  ncq
-- - gmI18N, gmServices and gmSchemaRevision are imported globally at the
--   database level now, don't include them in individual schema file anymore
--
-- Revision 1.42  2003/05/06 13:06:25  ncq
-- - pkey_ -> pk_
--
-- Revision 1.41  2003/05/05 12:40:03  ncq
-- - name is not a field of constituents anymore
--
-- Revision 1.40  2003/05/05 12:26:31  ncq
-- - remove comment on xref_id in script_drug, xref_id does not exist
--
-- Revision 1.39  2003/05/05 11:58:51  ncq
-- - audit_clinical -> clin_audit + use it
-- - clin_narrative now ancestor table + use it (as discussed with Ian)
--
-- Revision 1.38  2003/05/05 10:02:10  ihaywood
-- minor updates
--
-- Revision 1.37  2003/05/04 23:35:59  ncq
-- - major reworking to follow the formal EMR structure writeup
--
-- Revision 1.36  2003/05/03 00:44:40  ncq
-- - remove had_hypo from allergies table
--
-- Revision 1.35  2003/05/02 15:08:55  ncq
-- - episodes must have unique names (==description) per health issue
-- - remove cruft
-- - add not null to id_type in clin_encounter
-- - default id_comment in allergy to null
--
-- Revision 1.34  2003/05/01 15:06:29  ncq
-- - allergy.id_substance -> allergy.substance_code
--
-- Revision 1.33  2003/04/30 23:30:29  ncq
-- - v_i18n_patient_allergies
-- - new_allergy -> allergy_new
--
-- Revision 1.32  2003/04/29 12:38:32  ncq
-- - add not null to referencing constraints in episode/transactions
--
-- Revision 1.31  2003/04/28 21:40:40  ncq
-- - better indices
--
-- Revision 1.30  2003/04/28 20:56:16  ncq
-- - unclash "allergy" in hx type and type of allergic reaction + translations
-- - some useful indices
--
-- Revision 1.29  2003/04/25 12:43:52  ncq
-- - add grants
--
-- Revision 1.28  2003/04/25 12:32:39  ncq
-- - view on encounter types needs "as description"
--
-- Revision 1.27  2003/04/18 13:30:35  ncq
-- - add doc types
-- - update comment on allergy.id_substance
--
-- Revision 1.26  2003/04/17 20:20:11  ncq
-- - add source specific opaque substance/product identifier in table allergy
--
-- Revision 1.25  2003/04/12 15:34:49  ncq
-- - include the concept of aggregated clinical narrative
-- - consolidate history/physical exam tables
--
-- Revision 1.24  2003/04/09 14:47:17  ncq
-- - further tweaks on allergies tables
--
-- Revision 1.23  2003/04/09 13:50:29  ncq
-- - typos
--
-- Revision 1.22  2003/04/09 13:10:13  ncq
-- - _clinical_ -> _clin_
-- - streamlined episode/encounter/transaction
--
-- Revision 1.21  2003/04/07 12:28:24  ncq
-- - allergies table updated according to comments on resmed-de and gm-dev
--
-- Revision 1.20  2003/04/06 15:18:21  ncq
-- - can't reference _()ed fields in a view since it can't find the unique constraint in the underlying table
--
-- Revision 1.19  2003/04/06 15:10:05  ncq
-- - added some missing unique constraints
--
-- Revision 1.18  2003/04/06 14:51:40  ncq
-- - more cleanly separated data and schema
-- - first draft of allergies table
--
-- Revision 1.17  2003/04/02 13:37:56  ncq
-- - fixed a few more missing "primary key" on referenced "id serial"s
--
-- Revision 1.16  2003/04/02 12:31:07  ncq
-- - PostgreSQL 7.3 complained about referenced key enum_info_sources.id not being unique()d
-- -> make it primary key as it should be
--
-- Revision 1.15  2003/03/27 21:14:49  ncq
-- - cleanup, started work on Dutch structure
--
-- Revision 1.14  2003/01/20 20:10:12  ncq
-- - adapted to new i18n
--
-- Revision 1.13  2003/01/13 10:07:52  ihaywood
-- add free comment strings to script.
-- Start vaccination Hx tables
--
-- Revision 1.12  2003/01/05 13:05:51  ncq
-- - schema_revision -> gm_schema_revision
--
-- Revision 1.11  2002/12/22 01:26:16  ncq
-- - id_doctor -> id_provider + comment, typo fix
--
-- Revision 1.10  2002/12/14 08:55:17  ihaywood
-- new prescription tables -- fixed typos
--
-- Revision 1.9  2002/12/14 08:12:22  ihaywood
-- New prescription tables in gmclinical.sql
--
-- Revision 1.8  2002/12/06 08:50:51  ihaywood
-- SQL internationalisation, gmclinical.sql now internationalised.
--
-- Revision 1.7  2002/12/05 12:45:43  ncq
-- - added episode table, fixed typo
--
-- Revision 1.6  2002/12/01 13:53:09  ncq
-- - missing ; at end of schema tracking line
--
-- Revision 1.5  2002/11/23 13:18:09  ncq
-- - add "proper" metadata handling and schema revision tracking
--
