-- Project: GnuMed
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmclinical.sql,v $
-- $Revision: 1.110 $
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

select add_x_db_fk_def('xlnk_identity', 'xfk_identity', 'personalia', 'identity', 'id');
select add_table_for_audit('xlnk_identity');

comment on table xlnk_identity is
	'this is the one table with the unresolved identity(id)
	 foreign key, all other tables in this service link to
	 this table, depending upon circumstances one can add
	 dblink() verification or a true FK constraint (if "personalia"
	 is in the same database as "historica")';

-- ===================================================================
-- generic EMR structure
-- -------------------------------------------------------------------
create table clin_health_issue (
	id serial primary key,
	id_patient integer
		not null
		references xlnk_identity(xfk_identity)
		on update cascade
		on delete restrict,
	description varchar(128) default 'xxxDEFAULTxxx',
	unique (id_patient, description)
) inherits (audit_fields);

select add_table_for_audit('clin_health_issue');

comment on table clin_health_issue is
	'long-ranging, underlying health issue such as "mild immunodeficiency", "diabetes type 2"';
comment on column clin_health_issue.id_patient is
 	'id of patient this health issue relates to, should
	 be reference but might be outside our own database';
comment on column clin_health_issue.description is
	'descriptive name of this health issue, may change over time';

-- -------------------------------------------------------------------
-- episode related tables
-- -------------------------------------------------------------------
create table clin_episode (
	id serial primary key,
	id_health_issue integer not null references clin_health_issue(id),
	description varchar(128) default 'xxxDEFAULTxxx',
	unique (id_health_issue, description)
) inherits (audit_fields);

select add_table_for_audit('clin_episode');

comment on table clin_episode is
	'clinical episodes such as "recurrent Otitis media", "traffic accident 7/99", "Hepatitis B"';
comment on column clin_episode.id_health_issue is
	'health issue this episode is part of';
comment on column clin_episode.description is
	'descriptive name of this episode, may change over time; if
	 "xxxDEFAULTxxx" applications should display the most recently
	 associated diagnosis/month/year plus some marker for "default"';

-- unique names (descriptions) for episodes per health issue (e.g. per patient),
-- about the only reason for this table to exist is the description field such
-- as to allow arbitrary names for episodes, another reason is that explicit
-- recording of episodes removes the ambiguity that results from basing them
-- on start/end dates of bouts of care,

create table last_act_episode (
	id serial primary key,
	fk_episode integer
		unique
		not null
		references clin_episode(id),
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

-- -------------------------------------------------------------------
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
	fk_location integer,
	fk_provider integer,
	fk_type integer
		not null
		default 1
		references encounter_type(pk),
	description text
		default '',
	started timestamp with time zone
		not null
		default CURRENT_TIMESTAMP,
	last_affirmed timestamp with time zone
		not null
		default CURRENT_TIMESTAMP
--	,state text default 'affirmed'
);

-- remote foreign keys
select add_x_db_fk_def('clin_encounter', 'fk_location', 'personalia', 'org', 'id');
select add_x_db_fk_def('clin_encounter', 'fk_provider', 'personalia', 'staff', 'pk');

comment on table clin_encounter is
	'a clinical encounter between a person and the health care system';
comment on COLUMN clin_encounter.fk_patient is
	'PK of subject of care, should be PUPIC, actually';
comment on COLUMN clin_encounter.fk_location is
	'ID of location *of care*, e.g. where the provider is at';
comment on COLUMN clin_encounter.fk_provider is
	'PK of (main) provider of care';
comment on COLUMN clin_encounter.fk_type is
	'ID of type of this encounter';
comment on column clin_encounter.description is
	'descriptive name of this encounter, may change over time; if
	 "xxxDEFAULTxxx" applications should display "<date> (<provider>)"
	 plus some marker for "default"';

-- about the only reason for this table to exist is the id_type
-- field, otherwise one could just store the data in clin_root_item

create table curr_encounter (
	id serial primary key,
	id_encounter integer not null references clin_encounter(id),
	started timestamp with time zone not null default CURRENT_TIMESTAMP,
	last_affirmed timestamp with time zone not null default CURRENT_TIMESTAMP,
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
-- EMR item root with narrative aggregation
-- -------------------------------------------------------------------
create table clin_root_item (
	pk_item serial primary key,
	clin_when timestamp with time zone
		not null
		default CURRENT_TIMESTAMP,
	id_encounter integer
		not null
		references clin_encounter(id),
	fk_episode integer
		not null
		references clin_episode(id),
	narrative text,
	soap_cat text
		default null
		check(soap_cat in ('s', 'o', 'a', 'p'))
) inherits (audit_fields);

comment on TABLE clin_root_item is
	'ancestor table for clinical items of any kind, basic
	 unit of clinical information, do *not* store data in
	 here directly, use child tables,
	 contains all the clinical narrative aggregated for full
	 text search, ancestor for all tables that want to store
	 clinical free text';
comment on COLUMN clin_root_item.pk_item is
	'the primary key, not named "id" as usual since child tables
	 will have "id" primary keys already';
comment on column clin_root_item.clin_when is
	'when this clinical item became known, can be different from
	 when it was entered into the system (= audit_fields.modified_when)';
comment on COLUMN clin_root_item.id_encounter is
	'the encounter this item belongs to';
comment on COLUMN clin_root_item.fk_episode is
	'the episode this item belongs to';
comment on column clin_root_item.narrative is
	'each clinical item by default inherits a free text field for clinical narrative';

-- ============================================
-- specific EMR content tables: SOAP++
-- --------------------------------------------
create table clin_note (
	id serial primary key
) inherits (clin_root_item);

select add_table_for_audit('clin_note');

comment on TABLE clin_note is
	'Used to store clinical free text *not* associated with any other table.';

-- --------------------------------------------
create table clin_aux_note (
	pk serial primary key
) inherits (clin_root_item);

select add_table_for_audit('clin_aux_note');

comment on TABLE clin_aux_note is
	'Other tables link here if they need more free text fields.';

-- --------------------------------------------
create table _enum_hx_type (
	id serial primary key,
	description varchar(128) unique not null
);

comment on TABLE _enum_hx_type is
	'types of history taken during a clinical encounter';

-- --------------------------------------------
create table _enum_hx_source (
	id serial primary key,
	description varchar(128) unique not null
);

comment on table _enum_hx_source is
	'sources of clinical information: patient, relative, notes, correspondence';

-- --------------------------------------------
create table clin_history (
	id serial primary key,
	id_type integer not null references _enum_hx_type(id),
	id_source integer REFERENCES _enum_hx_source(id)
) inherits (clin_root_item);

-- narrative provided by clin_root_item

comment on TABLE clin_history is
	'narrative details of history taken during a clinical encounter';
comment on COLUMN clin_history.id_type is
	'the type of history taken';
comment on COLUMN clin_history.id_source is
	'who provided the details of this entry';

-- --------------------------------------------
create table clin_physical (
	id serial primary key
) inherits (clin_root_item);

-- narrative provided by clin_root_item

comment on TABLE clin_physical is
	'narrative details of physical exam during a clinical encounter';

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
-- FIXME: do we need lnk_vaccine2vacc_reg ?
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
select add_table_for_scoring('vacc_regime');

-- remote foreign keys:
select add_x_db_fk_def('vacc_regime', 'fk_recommended_by', 'reference', 'ref_source', 'id');

comment on table vacc_regime is
	'holds vaccination schedules/regimes/target diseases';
comment on column vacc_regime.fk_recommended_by is
	'organization recommending this vaccination';
comment on column vacc_regime.fk_indication is
	'vaccination indication this regime is targeted at';
comment on column vacc_regime.name is
	'regime name: schedule/disease/target bacterium...';

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
		check (((is_booster=true) and (seq_no is null)) or ((is_booster=false) and (seq_no > 0))),
	seq_no integer
		default null
		check (((is_booster=true) and (seq_no is null)) or ((is_booster=false) and (seq_no > 0))),
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
	'defines a given vaccination event';
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

select add_table_for_audit('vaccination');
select add_table_for_notifies('vaccination', 'vacc');

select add_x_db_fk_def('vaccination', 'fk_provider', 'personalia', 'staff', 'pk');

alter table vaccination alter column soap_cat set default 'p';

comment on table vaccination is
	'holds vaccinations actually given';

-- --------------------------------------------
-- this table will be even larger than vaccination ...
create table lnk_vacc2vacc_def (
	pk serial primary key,
	fk_vaccination integer
		not null
		references vaccination(id)
		on delete cascade
		on update cascade,
	fk_vacc_def integer
		not null
		references vacc_def(id)
		on delete restrict
		on update cascade,
	unique (fk_vaccination, fk_vacc_def)
) inherits (audit_fields);

comment on column lnk_vacc2vacc_def.fk_vacc_def is
	'the vaccination event a particular
	 vaccination is supposed to cover, allows to
	 link out-of-band vaccinations into regimes';

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
	value varchar(32) unique not null
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

select add_table_for_audit('allergy');
select add_table_for_notifies('allergy', 'allg');

alter table allergy alter column soap_cat set default 'o';

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
		references form_defs(pk)
		on update cascade
		on delete set null,
	form_name text not null
	-- clin_root_item.narrative used as status field
) inherits (clin_root_item);

select add_table_for_audit('form_instances');

comment on table form_instances is
	'instances of forms, like a log of all processed forms';
comment on column form_instances.fk_form_def is
	'points to the definition of this instance';
comment on column form_instances.form_name is
	'a string uniquely identifying the form template,
	 necessary for the audit trail';

-- --------------------------------------------
create table form_data (
	pk serial primary key,
	fk_instance integer
		not null
		references form_instances(pk)
		on update cascade
		on delete cascade,
	place_holder text not null,
	value text not null,
	unique(fk_instance, place_holder)
) inherits (audit_fields);

select add_table_for_audit('form_data');

comment on table form_data is
	'holds the values used in form instances, for
	 later re-use/validation';
comment on column form_data.fk_instance is
	'the form instance this value was used in';
comment on column form_data.place_holder is
	'the place holder in the form template that
	 should be replaced by this value';
comment on column form_data.value is
	'the value to replace the place holder with';

-- ============================================
-- diagnosis tables
-- --------------------------------------------
-- patient attached diagnosis
create table clin_working_diag (
	pk serial primary key,
	fk_progress_note integer
		default null
		references clin_aux_note(pk)
		on update cascade
		on delete restrict,
	laterality char
		default null
		check ((laterality in ('l', 'r', 'b', '?')) or (laterality is null)),
--	definity char
--		default 's'
--		check (definity in ('s', 'c', 'e')),
	is_chronic boolean
		not null
		default false,
	is_active boolean
		not null
		default true
		check (
			(is_chronic = false)
				or
			((is_chronic = true) and (is_active = true))
		),
	is_definite boolean
		not null
		default false,
	is_significant boolean
		not null
		default true
		check (
			(is_active = false)
				or
			((is_active = true) and (is_significant = true))
		),
	unique (narrative, fk_episode),
	unique (narrative, id_encounter)
) inherits (clin_root_item);

-- FIXME: trigger to insert/update/delete clin_aux_note fields on description update

select add_table_for_audit('clin_working_diag');

alter table clin_working_diag alter column soap_cat set default 'a';

comment on table clin_working_diag is
	'stores diagnoses attached to patients, may or may not be
	 linked to codes via lnk_diag2code';
comment on column clin_working_diag.narrative is
	'name of diagnosis';
comment on column clin_working_diag.fk_progress_note is
	'some additional clinical narrative such as approximate start';


-- "working set" of coded diagnoses
create table lnk_diag2code (
	pk serial primary key,
	description text
		not null,
	code text
		not null,
	xfk_coding_system text
		not null,
	unique (description, code, xfk_coding_system)
) inherits (audit_fields);

select add_table_for_audit('lnk_diag2code');
select add_x_db_fk_def('lnk_diag2code', 'xfk_coding_system', 'reference', 'ref_source', 'name_short');

comment on TABLE lnk_diag2code is
	'diagnoses as used clinically in patient charts linked to codes';
comment on column lnk_diag2code.description is
	'free text description of diagnosis';
comment on column lnk_diag2code.code is
	'the code in the coding system';
comment on column lnk_diag2code.xfk_coding_system is
	'the coding system used to code the diagnosis';


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
-- IMHO this needs considerably more thought
create table curr_medication (
	id serial primary key,
	-- administrative data
	started date not null,
	last_prescribed date not null,
	expires date not null,
	-- medical data
	brandname text default 'GENERIC',
	adjuvant text,
	db_origin text not null,
	db_xref text not null,
	atc_code varchar (32),
	amount_unit varchar (7) not null check (amount_unit in 
					('g', 'each', 'ml')),
	dose float,
	period integer not null,
	form varchar (20) not null check (form in 
			('spray', 'cap', 'tab', 'inh', 'neb', 'cream', 'syrup', 'lotion', 'drop', 'inj', 'oral liquid')), 
	directions text,
	prn boolean,
	SR boolean
) inherits (clin_root_item);

select add_table_for_audit ('curr_medication');

comment on table curr_medication is
'Representing what the patient is taking *now*, not a simple log
of prescriptions. The forms engine will record each script and all its fields
The audit mechanism will record all changes to this table.
 
Note the multiple redundancy of the stored drug data.
Applications should try in this order:
- internal database code
- brandname
- ATC code
- generic name(s) (in constituents)
';
comment on column curr_medication.started is
	'- when did patient start to take this medication
	 - in most cases the date of the first prescription
	   but not always
	 - for newly prescribed drugs identical to last_prescribed';
comment on column curr_medication.last_prescribed is
	'date last script written';
comment on column curr_medication.expires is
'date last script expires, for compliance checking';
comment on column curr_medication.prn is 'true if "pro re nata" (= as required)';
comment on column curr_medication.directions is 'free text for directions, such as "with food" etc';
comment on column curr_medication.adjuvant is 'free text describing adjuvants, such as "orange-flavoured" etc.';
comment on column curr_medication.brandname is 'the manufacturer''s own name for this drug';
comment on column curr_medication.db_origin is 'the drug database used to poulate this entry';
comment on column curr_medication.db_xref is 'the opaque identifier for this drug assigned by the source database';
comment on column curr_medication.atc_code is 'the Anatomic Therapeutic Chemical code for this drug';
comment on column curr_medication.amount_unit is 'the unit the dose is measured in. ''each'' for discrete objects like tablets';
comment on column curr_medication.dose is 'an array of doses describing how 
the drug is taken over the dosing cycle, for example 2 mane 2.5 nocte would be 
[2, 2.5], period=24. 2 one and 2.5 the next would be [2, 2.5] with 
period=48. Once a week would be [1] with period=168';
comment on column curr_medication.period is 'the length of the dosing cycle, in hours';
comment on column curr_medication.SR is 'true if the slow-release preparation is used';
comment on column curr_medication.form is 'the general form of the drug. Some approximation may be required from the manufacturer''s description';

-- --------------------------------------------
-- IMHO this does not belong in here
create table constituent
(
	genericname varchar (100) not null,
	amount float not null,
	amount_unit varchar (5) not null check (amount_unit in 
				('g', 'ml', 'mg', 'mcg', 'IU')),
	id_drug integer not null references curr_medication (id),
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
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmclinical.sql,v $', '$Revision: 1.110 $');

-- =============================================
-- $Log: gmclinical.sql,v $
-- Revision 1.110  2004-06-26 07:33:55  ncq
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
