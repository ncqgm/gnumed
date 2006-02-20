-- Project: GNUmed
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmclinical.sql,v $
-- $Revision: 1.180 $
-- license: GPL
-- author: Ian Haywood, Horst Herb, Karsten Hilbert

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
-- EMR items root with narrative aggregation
-- -------------------------------------------------------------------
create table clin.clin_root_item (
	pk_item serial primary key,
	clin_when timestamp with time zone
		not null
		default CURRENT_TIMESTAMP,
	fk_encounter integer
		not null
		references clin.encounter(pk)
		on update cascade
		on delete restrict,
	fk_episode integer
		not null
		references clin.episode(pk)
		on update cascade
		on delete restrict,
	narrative text,
	soap_cat text
		not null
		check(lower(soap_cat) in ('s', 'o', 'a', 'p'))
) inherits (audit.audit_fields);

-- --------------------------------------------
create table clin.clin_item_type (
	pk serial primary key,
	type text
		default 'history'
		unique
		not null,
	code text
		default 'Hx'
		unique
		not null
) inherits (audit.audit_fields);

-- --------------------------------------------
create table clin.lnk_type2item (
	pk serial primary key,
	fk_type integer
		not null
		references clin.clin_item_type(pk)
		on update cascade
		on delete cascade,
	fk_item integer
		not null
--		references clin.clin_root_item(pk_item)
--		on update cascade
--		on delete cascade
		,
	unique (fk_type, fk_item)
) inherits (audit.audit_fields);

-- ============================================
-- specific EMR content tables: SOAP++
-- --------------------------------------------
-- soap cats
create table clin.soap_cat_ranks (
	pk serial primary key,
	rank integer
		not null
		check (rank in (1,2,3,4)),
	soap_cat character(1)
		not null
		check (lower(soap_cat) in ('s', 'o', 'a', 'p'))
);

-- narrative
create table clin.clin_narrative (
	pk serial primary key
) inherits (clin.clin_root_item);

alter table clin.clin_narrative add foreign key (fk_encounter)
		references clin.encounter(pk)
		on update cascade
		on delete restrict;

alter table clin.clin_narrative add foreign key (fk_episode)
		references clin.episode(pk)
		on update cascade
		on delete restrict;

alter table clin.clin_narrative add constraint narrative_neither_null_nor_empty
	check (trim(coalesce(narrative, '')) != '');

-- --------------------------------------------
-- coded narrative
create table clin.coded_narrative (
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
) inherits (audit.audit_fields);

-- --------------------------------------------
-- general FH storage
create table clin.hx_family_item (
	pk serial primary key,
	fk_narrative_condition integer
		default null
		references clin.clin_narrative(pk)
		on update cascade
		on delete restrict,
	fk_relative integer
		default null
		references clin.xlnk_identity(xfk_identity)
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
) inherits (audit.audit_fields);

alter table clin.hx_family_item add constraint link_or_know_condition
	check (
		(fk_narrative_condition is not null and condition is null)
			or
		(fk_narrative_condition is null and condition is not null)
	);

alter table clin.hx_family_item add constraint link_or_know_relative
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

-- patient linked FH
create table clin.clin_hx_family (
	pk serial primary key,
	fk_hx_family_item integer
		not null
		references clin.hx_family_item(pk)
		on update cascade
		on delete restrict
) inherits (clin.clin_root_item);

alter table clin.clin_hx_family add foreign key (fk_encounter)
		references clin.encounter(pk)
		on update cascade
		on delete restrict;
alter table clin.clin_hx_family add foreign key (fk_episode)
		references clin.episode(pk)
		on update cascade
		on delete restrict;
alter table clin.clin_hx_family add constraint narrative_neither_null_nor_empty
	check (trim(coalesce(narrative, '')) != '');
-- FIXME: constraint trigger has_type(fHx)

-- --------------------------------------------
-- patient attached diagnoses
create table clin.clin_diag (
	pk serial primary key,
	fk_narrative integer
		unique
		not null
		references clin.clin_narrative(pk)
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
) inherits (audit.audit_fields);

alter table clin.clin_diag add constraint if_active_then_relevant
	check (
		(is_active = false)
			or
		((is_active = true) and (clinically_relevant = true))
	);
-- not sure about that one:
--alter table clin.clin_diag add constraint if_chronic_then_relevant
--	check (
--		(is_chronic = false)
--			or
--		((is_chronic = true) and (clinically_relevant = true))
--	);

-- --------------------------------------------
create table clin.clin_aux_note (
	pk serial primary key
) inherits (clin.clin_root_item);

alter table clin.clin_aux_note add foreign key (fk_encounter)
		references clin.encounter(pk)
		on update cascade
		on delete restrict;
alter table clin.clin_aux_note add foreign key (fk_episode)
		references clin.episode(pk)
		on update cascade
		on delete restrict;

-- ============================================
-- allergies tables
create table clin.allergy_state (
	id serial primary key,
	fk_patient integer
		unique
		not null
		references clin.xlnk_identity(xfk_identity)
		on update cascade
		on delete restrict,
	has_allergy integer
		default null
		check (has_allergy in (null, -1, 0, 1))
) inherits (audit.audit_fields);

-- --------------------------------------------
create table clin._enum_allergy_type (
	id serial primary key,
	value text unique not null
);

-- --------------------------------------------
create table clin.allergy (
	id serial primary key,
	substance text not null,
	substance_code text default null,
	generics text default null,
	allergene text default null,
	atc_code text default null,
	id_type integer
		not null
		references clin._enum_allergy_type(id),
	generic_specific boolean default false,
	definite boolean default false
) inherits (clin.clin_root_item);

-- narrative provided by clin.clin_root_item

alter table clin.allergy add foreign key (fk_encounter)
	references clin.encounter(pk)
	on update cascade
	on delete restrict;
alter table clin.allergy add foreign key (fk_episode)
	references clin.episode(pk)
	on update cascade
	on delete restrict;
alter table clin.allergy alter column soap_cat set default 'o';

-- ============================================
-- form instance tables
-- --------------------------------------------
create table clin.form_instances (
	pk serial primary key,
	fk_form_def integer
		not null
		references form_defs(pk)
		on update cascade
		on delete restrict,
	form_name text not null
) inherits (clin.clin_root_item);

-- FIXME: remove clin_root_item, not audited, lnk_form_instance2episode

alter table clin.form_instances add foreign key (fk_encounter)
		references clin.encounter(pk)
		on update cascade
		on delete restrict;
alter table clin.form_instances add foreign key (fk_episode)
		references clin.episode(pk)
		on update cascade
		on delete restrict;
alter table clin.form_instances add constraint form_is_plan
	check (soap_cat='p');

-- --------------------------------------------
create table clin.form_data (
	pk serial primary key,
	fk_instance integer
		not null
		references clin.form_instances(pk)
		on update cascade
		on delete restrict,
	fk_form_field integer
		not null
		references public.form_fields(pk)
		on update cascade
		on delete restrict,
	value text not null,
	unique(fk_instance, fk_form_field)
) inherits (audit.audit_fields);

-- ============================================
-- medication tables
create table clin.clin_medication (
	pk serial primary key,
	-- administrative
	last_prescribed date
		not null
		default CURRENT_DATE,
	fk_last_script integer
		default null
		references clin.form_instances(pk)
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
) inherits (clin.clin_root_item);

alter table clin.clin_medication add foreign key (fk_encounter)
		references clin.encounter(pk)
		on update cascade
		on delete restrict;
alter table clin.clin_medication add foreign key (fk_episode)
		references clin.episode(pk)
		on update cascade
		on delete restrict;
alter table clin.clin_medication add constraint medication_is_plan
	check (soap_cat='p');
alter table clin.clin_medication add constraint brand_or_generic_required
	check ((brandname is not null) or (generic is not null));
alter table clin.clin_medication add constraint prescribed_after_started
	check (last_prescribed >= clin_when::date);
alter table clin.clin_medication add constraint discontinued_after_prescribed
	check (discontinued >= last_prescribed);

-- ===================================================================
-- following tables not yet converted to EMR structure ...
-- -------------------------------------------------------------------

-- =============================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmclinical.sql,v $', '$Revision: 1.180 $');

-- =============================================
-- $Log: gmclinical.sql,v $
-- Revision 1.180  2006-02-20 10:22:32  ncq
-- - indexing on clin.clin_narrative(narrative) directly was prone to
--   buffer overrun since it's a text field of unlimited length, so,
--   index on md5(narrative) now
--
-- Revision 1.179  2006/02/10 14:08:58  ncq
-- - factor out EMR structure clinical schema into its own set of files
--
-- Revision 1.178  2006/02/08 15:15:39  ncq
-- - factor our vaccination stuff into its own set of files
-- - remove clin.lnk_vacc_ind2code in favour of clin.coded_term usage
-- - improve comments as discussed on the list
--
-- Revision 1.177  2006/01/06 10:12:02  ncq
-- - add missing grants
-- - add_table_for_audit() now in "audit" schema
-- - demographics now in "dem" schema
-- - add view v_inds4vaccine
-- - move staff_role from clinical into demographics
-- - put add_coded_term() into "clin" schema
-- - put German things into "de_de" schema
--
-- Revision 1.176  2006/01/05 16:04:37  ncq
-- - move auditing to its own schema "audit"
--
-- Revision 1.175  2006/01/01 20:41:06  ncq
-- - move vacc_def constraints around
-- - add trigger constraint to make sure there's always base
--   immunization definitions for boosters
--
-- Revision 1.174  2005/12/29 21:48:09  ncq
-- - clin.vaccine.id -> pk
-- - remove clin.vaccine.last_batch_no
-- - add clin.vaccine_batches
-- - adjust test data and country data
--
-- Revision 1.173  2005/12/06 13:26:55  ncq
-- - clin.clin_encounter -> clin.encounter
-- - also id -> pk
--
-- Revision 1.172  2005/12/05 19:05:59  ncq
-- - clin_episode -> episode
--
-- Revision 1.171  2005/12/04 09:48:02  ncq
-- - clin_health_issue -> health_issue (and id -> pk)
-- - remove constituent
-- - move referral to AU schema
-- - comment on forms_data re Ian's suggestions
--
-- Revision 1.170  2005/11/27 13:02:07  ncq
-- - constituent/referral commented out for now
--
-- Revision 1.169  2005/11/25 15:07:28  ncq
-- - create schema "clin" and move all things clinical into it
--
-- Revision 1.168  2005/11/11 23:06:12  ncq
-- - typo
--
-- Revision 1.167  2005/09/25 17:48:23  ncq
-- - remove last_act_episode, it's not used
--
-- Revision 1.166  2005/09/25 01:00:47  ihaywood
-- bugfixes
--
-- remember 2.6 uses "import wx" not "from wxPython import wx"
-- removed not null constraint on clin_encounter.rfe as has no value on instantiation
-- client doesn't try to set clin_encounter.description as it doesn't exist anymore
--
-- Revision 1.165  2005/09/22 15:40:43  ncq
-- - clin_encounter
--   - aoe must be default null because we don't know
--     it yet when starting an encounter
--   - improve comments
--   - remove fk_provider
--
-- Revision 1.164  2005/09/21 10:21:16  ncq
-- - include waiting list
--
-- Revision 1.163  2005/09/19 16:19:58  ncq
-- - cleanup
-- - support rfe/aoe in clin_encounter and adjust to that
--
-- Revision 1.162  2005/08/19 08:23:04  ncq
-- - comment update
--
-- Revision 1.161  2005/07/14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.160  2005/06/19 13:33:51  ncq
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
