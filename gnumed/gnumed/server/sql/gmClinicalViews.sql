-- project: GNUmed

-- purpose: views for easier clinical data access
-- author: Karsten Hilbert
-- license: GPL v2 or later (details at http://gnu.org)

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmClinicalViews.sql,v $
-- $Id: gmClinicalViews.sql,v 1.184 2006-06-20 15:49:30 ncq Exp $

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
-- clin.clin_root_item
comment on TABLE clin.clin_root_item is
	'ancestor table for clinical items of any kind, basic
	 unit of clinical information, do *not* store data in
	 here directly, use child tables,
	 contains all the clinical narrative aggregated for full
	 text search, ancestor for all tables that want to store
	 clinical free text';
comment on COLUMN clin.clin_root_item.pk_item is
	'the primary key, not named "id" or "pk" as usual since child
	 tables will have "id"/"pk"-named primary keys already and
	 we would get duplicate columns while inheriting from this
	 table';
comment on column clin.clin_root_item.clin_when is
	'when this clinical item became known, can be different from
	 when it was entered into the system (= audit.audit_fields.modified_when)';
comment on COLUMN clin.clin_root_item.fk_encounter is
	'the encounter this item belongs to';
comment on COLUMN clin.clin_root_item.fk_episode is
	'the episode this item belongs to';
comment on column clin.clin_root_item.narrative is
	'each clinical item by default inherits a free text field for clinical narrative';
comment on column clin.clin_root_item.soap_cat is
	'each clinical item must be in one of the S, O, A, P categories';

-- clin.clin_item_type --
select audit.add_table_for_audit('clin', 'clin_item_type');

comment on table clin.clin_item_type is
	'stores arbitrary types for tagging clinical items';
comment on column clin.clin_item_type.type is
	'the full name of the item type such as "family history"';
comment on column clin.clin_item_type.code is
	'shorthand for the type, eg "FHx"';

-- clin.lnk_type2item --
select audit.add_table_for_audit('clin', 'lnk_type2item');

comment on table clin.lnk_type2item is
	'allow to link many-to-many between clin.clin_root_item and clin.clin_item_type';
-- FIXME: recheck for 8.0
comment on column clin.lnk_type2item.fk_item is
	'the item this type is linked to,
	 since PostgreSQL apparently cannot reference a value
	 inserted from a child table (?) we must simulate
	 referential integrity checks with a custom trigger,
	 this, however, does not deal with update/delete
	 cascading :-(';

-- clin.clin_narrative
select audit.add_table_for_audit('clin', 'clin_narrative');

comment on TABLE clin.clin_narrative is
	'Used to store clinical free text *not* associated
	 with any other table. Used to implement a simple
	 SOAP structure. Also other tags can be associated
	 via link tables.';
comment on column clin.clin_narrative.clin_when is
	'when did the item reach clinical reality';

alter table clin.clin_narrative add foreign key (fk_encounter)
		references clin.encounter(pk)
		on update cascade
		on delete restrict;

alter table clin.clin_narrative add foreign key (fk_episode)
		references clin.episode(pk)
		on update cascade
		on delete restrict;

alter table clin.clin_narrative drop constraint if exists narrative_neither_null_nor_empty;

alter table clin.clin_narrative add constraint narrative_neither_null_nor_empty
	check (trim(coalesce(narrative, '')) != '');

-- NOT NEEDED, index works just fine
-- this trigger is like a constraint UNIQUE (fk_encounter, narrative, soap_cat),
-- but it uses md5(narrative) to avoid overflowing index buffers
--create or replace function clin.is_unique_narrative()
--	returns trigger
--	language 'plpgsql'
--	as '
--BEGIN
--	if TG_OP = ''UPDATE'' then
--		-- allow updating same row without content change
--		if NEW.pk = OLD.PK then
--			return NEW;
--		end if;
--	end if;
--	perform 1 from clin.clin_narrative c where
--		c.soap_cat = NEW.soap_cat and
--		c.fk_encounter = NEW.fk_encounter and
--		c.fk_episode = NEW.fk_episode and
--		md5(c.narrative) = md5(NEW.narrative);
--	if found then
--		raise exception ''clin.is_unique_narrative(): Cannot duplicate narrative in same episode/encounter/SOAP category.'';
--		return null;
--	end if;
--	return NEW;
--	END;
-- ';

--create trigger tr_narrative_no_duplicate
--	before update or insert on clin.clin_narrative
--	for each row execute procedure clin.is_unique_narrative();

-- -- clin.operation --
select audit.add_table_for_audit('clin', 'operation');

comment on table clin.operation is
	'data about operations a patient had, links to clin.health_issue,
	 use clin.health_issue.age_noted for date of operation';
comment on column clin.operation.fk_health_issue is
	'which clin.health_issue this row refers to';
comment on column clin.operation.fk_encounter is
	'during which encounter we learned of this';
comment on column clin.operation.clin_where is
	'where did this operation take place';

-- clin.coded_term
select audit.add_table_for_audit('clin', 'coded_narrative');
--select add_x_db_fk_def('coded_narrative', 'xfk_coding_system', 'reference', 'ref_source', 'name_short');

comment on table clin.coded_narrative is
	'associates codes with text snippets
	 which may be in use in clinical tables';
comment on column clin.coded_narrative.term is
	'the text snippet that is to be coded';
comment on column clin.coded_narrative.code is
	'the code in the coding system';
comment on column clin.coded_narrative.xfk_coding_system is
	'the coding system used to code the text snippet';

-- clin.hx_family_items --
select audit.add_table_for_audit('clin', 'hx_family_item');

comment on table clin.hx_family_item is
	'stores family history items independent of the patient,
	 this is out-of-EMR so that several patients can link to it';
comment on column clin.hx_family_item.fk_narrative_condition is
	'can point to a narrative item of a relative if in database';
comment on column clin.hx_family_item.fk_relative is
	'foreign key to relative if in database';
comment on column clin.hx_family_item.name_relative is
	'name of the relative if not in database';
comment on column clin.hx_family_item.dob_relative is
	'DOB of relative if not in database';
comment on column clin.hx_family_item.condition is
	'narrative holding the condition the relative suffered from,
	 must be NULL if fk_narrative_condition is not';
comment on column clin.hx_family_item.age_noted is
	'at what age the relative acquired the condition';
comment on column clin.hx_family_item.age_of_death is
	'at what age the relative died';
comment on column clin.hx_family_item.is_cause_of_death is
	'whether relative died of this problem, Richard
	 suggested to allow that several times per relative';

-- clin.clin_hx_family --
select audit.add_table_for_audit('clin', 'clin_hx_family');

comment on table clin.clin_hx_family is
	'stores family history for a given patient';
comment on column clin.clin_hx_family.clin_when is
	'when the family history item became known';
comment on column clin.clin_hx_family.fk_encounter is
	'encounter during which family history item became known';
comment on column clin.clin_hx_family.fk_episode is
	'episode to which family history item is of importance';
comment on column clin.clin_hx_family.narrative is
	'how is the afflicted person related to the patient';
comment on column clin.clin_hx_family.soap_cat is
	'as usual, must be NULL if fk_narrative_condition is not but
	 this is not enforced and only done in the view';

-- clin.clin_diag --
select audit.add_table_for_audit('clin', 'clin_diag');

comment on table clin.clin_diag is
	'stores additional detail on those clin.clin_narrative
	 rows where soap_cat=a that are true diagnoses,
	 true diagnoses DO have a code from one of the coding systems';
comment on column clin.clin_diag.is_chronic is
	'whether this diagnosis is chronic, eg. no complete
	 cure is to be expected, regardless of whether it is
	 *active* right now (think of active/non-active phases
	 of Multiple Sclerosis which is sure chronic)';
comment on column clin.clin_diag.is_active is
	'whether diagnosis is currently active or dormant';
comment on column clin.clin_diag.clinically_relevant is
	'whether this diagnosis is considered clinically
	 relevant, eg. significant;
	 currently active diagnoses are considered to
	 always be relevant, while inactive ones may
	 or may not be';

-- clin.clin_aux_note --
select audit.add_table_for_audit('clin', 'clin_aux_note');

comment on TABLE clin.clin_aux_note is
	'Other tables link to this if they need more free text fields.';

-- allergy_state --
select audit.add_table_for_audit('clin', 'allergy_state');

comment on column clin.allergy_state.has_allergy is
	'patient allergenic state:
	 - null: unknown, not asked, no data available
	 - -1: unknown, asked, no data obtained
	 - 0:  known, asked, has no known allergies
	 - 1:  known, asked, does have allergies
	';

-- allergy --
select audit.add_table_for_audit('clin', 'allergy');
-- delete from notifying_tables where table_name = 'allergy';
select add_table_for_notifies('clin', 'allergy', 'allg');

comment on table clin.allergy is
	'patient allergy details';
comment on column clin.allergy.substance is
	'real-world name of substance the patient reacted to, brand name if drug';
comment on column clin.allergy.substance_code is
	'data source specific opaque product code; must provide a link
	 to a unique product/substance in the database in use; should follow
	 the parseable convention of "<source>::<source version>::<identifier>",
	 e.g. "MIMS::2003-1::190" for Zantac; it is left as an exercise to the
	 application to know what to do with this information';
comment on column clin.allergy.generics is
	'names of generic compounds if drug; brand names change/disappear, generic names do not';
comment on column clin.allergy.allergene is
	'name of allergenic ingredient in substance if known';
comment on column clin.allergy.atc_code is
	'ATC code of allergene or substance if approprate, applicable for penicilline, not so for cat fur';
comment on column clin.allergy.id_type is
	'allergy/sensitivity';
comment on column clin.allergy.generic_specific is
	'only meaningful for *drug*/*generic* reactions:
	 1) true: applies to one in "generics" forming "substance",
			  if more than one generic listed in "generics" then
			  "allergene" *must* contain the generic in question;
	 2) false: applies to drug class of "substance";';
comment on column clin.allergy.definite is
	'true: definite, false: not definite';
comment on column clin.allergy.narrative is
	'used as field "reaction"';

-- clin.form_instances --
--select add_x_db_fk_def('form_instances', 'xfk_form_def', 'reference', 'form_defs', 'pk');

select audit.add_table_for_audit('clin', 'form_instances');

comment on table clin.form_instances is
	'instances of forms, like a log of all processed forms';
comment on column clin.form_instances.fk_form_def is
	'points to the definition of this instance,
	 this FK will fail once we start separating services,
	 make it into a x_db_fk then';
comment on column clin.form_instances.form_name is
	'a string uniquely identifying the form template,
	 necessary for the audit trail';
comment on column clin.form_instances.narrative is
	'can be used as a status field, eg. "printed", "faxed" etc.';

-- clin.form_data --
--select add_x_db_fk_def('form_data', 'xfk_form_field', 'reference', 'form_fields', 'pk');

select audit.add_table_for_audit('clin', 'form_data');

comment on table clin.form_data is
	'holds the values used in form instances, for
	 later re-use/validation';
comment on column clin.form_data.fk_instance is
	'the form instance this value was used in';
comment on column clin.form_data.fk_form_field is
	'points to the definition of the field in the form
	 which in turn defines the place holder in the
	 template to replace with <value>';
comment on column clin.form_data.value is
	'the value to replace the place holder with';

-- clin.clin_medication --
select audit.add_table_for_audit('clin', 'clin_medication');

comment on table clin.clin_medication is
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
comment on column clin.clin_medication.clin_when is
	'used as "started" column
	 - when did patient start to take this medication
	 - in many cases date of first prescription - but not always
	 - for newly prescribed drugs identical to last_prescribed';
comment on column clin.clin_medication.narrative is
	'used as "prescribed_for" column
	 - use to specify intent beyond treating issue at hand';
comment on column clin.clin_medication.last_prescribed is
	'date last script written for this medication';
comment on column clin.clin_medication.fk_last_script is
	'link to the most recent script by which this drug
	 was prescribed';
comment on column clin.clin_medication.discontinued is
	'date at which medication was *discontinued*,
	 note that the date when a script *expires*
	 should be calculatable';
comment on column clin.clin_medication.brandname is
	'the brand name of this drug under which it is
	 marketed by the manufacturer';
comment on column clin.clin_medication.generic is
	'the generic name of the active substance';
comment on column clin.clin_medication.adjuvant is
	'free text describing adjuvants, such as "orange-flavoured" etc.';
comment on column clin.clin_medication.dosage_form is
	'the form the drug is delivered in, eg liquid, cream, table, etc.';
comment on column clin.clin_medication.ufk_drug is
	'the identifier for this drug in the source database,
	 may or may not be an opaque value as regards GNUmed';
comment on column clin.clin_medication.drug_db is
	'the drug database used to populate this entry';
comment on column clin.clin_medication.atc_code is
	'the Anatomic Therapeutic Chemical code for this drug,
	 used to compute possible substitutes';
comment on column clin.clin_medication.is_CR is
	'Controlled Release. Some drugs are marketed under the
	 same name although one is slow release while the other
	 is normal release.';
comment on column clin.clin_medication.dosage is
	'an array of doses describing how the drug is taken
	 over the dosing cycle, for example:
	  - 2 mane 2.5 nocte would be [2, 2.5], period="24 hours"
	  - 2 one and 2.5 the next would be [2, 2.5], period="2 days"
	  - once a week would be [1] with period="1 week"';
comment on column clin.clin_medication.period is
	'the length of the dosing cycle, in hours';
comment on column clin.clin_medication.dosage_unit is
	'the unit the dosages are measured in,
	 "each" for discrete objects like tablets';
comment on column clin.clin_medication.directions is
	'free text for patient/pharmacist directions,
	 such as "with food" etc';
comment on column clin.clin_medication.is_prn is
	'true if "pro re nata" (= as required)';

-- reviewed_test_results --
comment on table clin.reviewed_test_results is
	'review table for test results';

-- =============================================
drop index if exists clin.idx_cri_encounter;
drop index if exists clin.idx_cri_episode;

drop index if exists clin.idx_clnarr_encounter;
drop index if exists clin.idx_clnarr_episode;
drop index if exists clin.idx_clnarr_unique;

drop index if exists clin.idx_clanote_encounter;
drop index if exists clin.idx_clanote_episode;

drop index if exists clin.idx_vacc_encounter;
drop index if exists clin.idx_vacc_episode;

drop index if exists clin.idx_allg_encounter;
drop index if exists clin.idx_allg_episode;

drop index if exists clin.idx_formi_encounter;
drop index if exists clin.idx_formi_episode;

drop index if exists clin.idx_cmeds_encounter;
drop index if exists clin.idx_cmeds_episode;

drop index if exists clin.idx_ref_encounter;
drop index if exists clin.idx_ref_episode;

drop index if exists clin.idx_tres_encounter;
drop index if exists clin.idx_tres_episode;

drop index if exists clin.idx_lreq_encounter;
drop index if exists clin.idx_lreq_episode;

-- clin.clin_root_item & children indices
create index idx_cri_encounter on clin.clin_root_item(fk_encounter);
create index idx_cri_episode on clin.clin_root_item(fk_episode);

create index idx_clnarr_encounter on clin.clin_narrative(fk_encounter);
create index idx_clnarr_episode on clin.clin_narrative(fk_episode);
create unique index idx_clnarr_unique on clin.clin_narrative(fk_encounter, fk_episode, soap_cat, modified_by, md5(narrative));

create index idx_clanote_encounter on clin.clin_aux_note(fk_encounter);
create index idx_clanote_episode on clin.clin_aux_note(fk_episode);

create index idx_vacc_encounter on clin.vaccination(fk_encounter);
create index idx_vacc_episode on clin.vaccination(fk_episode);

create index idx_allg_encounter on clin.allergy(fk_encounter);
create index idx_allg_episode on clin.allergy(fk_episode);

create index idx_formi_encounter on clin.form_instances(fk_encounter);
create index idx_formi_episode on clin.form_instances(fk_episode);

create index idx_cmeds_encounter on clin.clin_medication(fk_encounter);
create index idx_cmeds_episode on clin.clin_medication(fk_episode);

create index idx_tres_encounter on clin.test_result(fk_encounter);
create index idx_tres_episode on clin.test_result(fk_episode);

create index idx_lreq_encounter on clin.lab_request(fk_encounter);
create index idx_lreq_episode on clin.lab_request(fk_episode);

-- =============================================
-- narrative
drop index if exists clin.idx_narr_soap;
--drop index if exists clin.idx_narr_s;
--drop index if exists clin.idx_narr_o;
--drop index if exists clin.idx_narr_a;
--drop index if exists clin.idx_narr_p;

create index idx_narr_soap on clin.clin_narrative(soap_cat);
-- comment those out for now as such queries aren't particularly common
--create index idx_narr_s on clin.clin_narrative(soap_cat) where soap_cat='s';
--create index idx_narr_o on clin.clin_narrative(soap_cat) where soap_cat='o';
--create index idx_narr_a on clin.clin_narrative(soap_cat) where soap_cat='a';
--create index idx_narr_p on clin.clin_narrative(soap_cat) where soap_cat='p';

-- clin.clin_medication
drop index if exists clin.idx_clin_medication;

create index idx_clin_medication on clin.clin_medication(discontinued) where discontinued is not null;

-- =============================================
-- clin_root_item stuff
drop function if exists clin.f_announce_clin_item_mod() cascade;

create function clin.f_announce_clin_item_mod()
	returns trigger
	as '
declare
	episode_id integer;
	patient_id integer;
begin
	-- get episode ID
	if TG_OP = ''DELETE'' then
		episode_id := OLD.fk_episode;
	else
		episode_id := NEW.fk_episode;
	end if;
	-- track back to patient ID
	select into patient_id pk_patient
		from clin.v_pat_episodes vpep
		where vpep.pk_episode = episode_id
		limit 1;
	-- now, execute() the NOTIFY
	execute ''notify "item_change_db:'' || patient_id || ''"'';
	return NULL;
end;
' language 'plpgsql';

create trigger TR_clin_item_mod
	after insert or delete or update
	on clin.clin_root_item
	for each row
		execute procedure clin.f_announce_clin_item_mod()
;

-- ---------------------------------------------
-- protect from direct inserts/updates/deletes which the
-- inheritance system can't handle properly
drop function if exists clin.f_protect_clin_root_item() cascade;

create function clin.f_protect_clin_root_item() returns trigger as '
begin
	raise exception ''INSERT/DELETE on <clin_root_item> not allowed.'';
	return NULL;
end;
' language 'plpgsql';

create rule clin_ritem_no_ins as
	on insert to clin.clin_root_item
	do instead select clin.f_protect_clin_root_item();

create rule clin_ritem_no_del as
	on delete to clin.clin_root_item
	do instead select clin.f_protect_clin_root_item();

-- ---------------------------------------------
drop view if exists clin.v_pat_items cascade;

create view clin.v_pat_items as
select
--	extract(epoch from cri.clin_when) as age,
	cri.modified_when as modified_when,
	cri.modified_by as modified_by,
	cri.clin_when as clin_when,
	case cri.row_version
		when 0 then false
		else true
	end as is_modified,
	vpep.pk_patient as pk_patient,
	cri.pk_item as pk_item,
	cri.fk_encounter as pk_encounter,
	cri.fk_episode as pk_episode,
	vpep.pk_health_issue as pk_health_issue,
	cri.soap_cat as soap_cat,
	cri.narrative as narrative,
	pgc.relname as src_table
from
	clin.clin_root_item cri,
	clin.v_pat_episodes vpep,
	pg_class pgc
where
	vpep.pk_episode=cri.fk_episode
		and
	cri.tableoid=pgc.oid
;

-- ==========================================================
-- measurements stuff

drop view if exists clin.v_test_type_unified cascade;

create view clin.v_test_type_unified as
select
	ttu.pk as pk_test_type_unified,
	ltt2ut.fk_test_type as pk_test_type,
	ttu.code as code_unified,
	ttu.name as name_unified,
	ttu.coding_system as coding_system_unified,
	ttu.comment as comment_unified,
	ltt2ut.pk as pk_lnk_ttype2unified_type
from
	clin.test_type_unified ttu,
	clin.lnk_ttype2unified_type ltt2ut
where
	ltt2ut.fk_test_type_unified=ttu.pk
;

comment on view clin.v_test_type_unified is
	'denormalized view of test_type_unified and link table to test_type';

create view clin.v_unified_test_types as
select
	ttu0.pk as pk_test_type,
	-- unified test_type
	coalesce(ttu0.code_unified, ttu0.code) as unified_code,
	coalesce(ttu0.name_unified, ttu0.name) as unified_name,
	-- original test_type
	ttu0.code as code_tt,
	ttu0.name as name_tt,
	ttu0.coding_system as coding_system_tt,
	ttu0.comment as comment_tt,
	ttu0.conversion_unit as conversion_unit,
	-- unified version thereof
	ttu0.code_unified,
	ttu0.name_unified,
	ttu0.coding_system_unified,
	ttu0.comment_unified,
	-- admin links
	ttu0.fk_test_org as pk_test_org,
	ttu0.pk_test_type_unified,
	ttu0.pk_lnk_ttype2unified_type
from
	(clin.test_type tt1 left outer join clin.v_test_type_unified vttu1 on (tt1.pk=vttu1.pk_test_type)) ttu0
;

comment on view clin.v_unified_test_types is
	'provides a view of test types aggregated under their
	 corresponding unified name if any, if not linked to a
	 unified test type name the original name is used';

create view clin.v_test_org_profile as
select
	torg.pk as pk_test_org,
	torg.internal_name,
	vttu.pk_test_type,
	vttu.code_tt as test_code,
	vttu.coding_system_tt,
	vttu.coding_system_unified,
	vttu.unified_code,
	vttu.name_tt as test_name,
	vttu.unified_name,
	vttu.conversion_unit,
	vttu.comment_tt as test_comment,
	vttu.comment_unified,
	torg.comment as org_comment,
	torg.fk_org as pk_org
from
	clin.test_org torg,
	clin.v_unified_test_types vttu
where
	vttu.pk_test_org=torg.pk
;

comment on view clin.v_test_org_profile is
	'the tests a given test org provides';


create view clin.v_test_results as
select
	-- v_pat_episodes
	vpe.pk_patient as pk_patient,
	-- test_result
	tr.pk as pk_test_result,
	-- unified
	tr.clin_when,
	vttu.unified_code,
	vttu.unified_name,
	case when coalesce(trim(both from tr.val_alpha), '') = ''
		then tr.val_num::text
		else case when tr.val_num is null
			then tr.val_alpha
			else tr.val_num::text || ' (' || tr.val_alpha || ')'
		end
	end as unified_val,
	case when tr.val_target_min is null
		then tr.val_normal_min
		else tr.val_target_min
	end as unified_target_min,
	case when tr.val_target_max is null
		then tr.val_normal_max
		else tr.val_target_max
	end as unified_target_max,
	case when tr.val_target_range is null
		then tr.val_normal_range
		else tr.val_target_range
	end as unified_target_range,
	tr.soap_cat,
	coalesce(tr.narrative, '') as comment,
	-- test result data
	tr.val_num,
	tr.val_alpha,
	tr.val_unit,
	vttu.conversion_unit,
	tr.val_normal_min,
	tr.val_normal_max,
	tr.val_normal_range,
	tr.val_target_min,
	tr.val_target_max,
	tr.val_target_range,
--	tr.reviewed_by_clinician,
--	tr.clinically_relevant,
	tr.abnormality_indicator,
	tr.norm_ref_group,
	tr.note_provider,
	tr.material,
	tr.material_detail,
	-- test type data
	vttu.code_tt,
	vttu.name_tt,
	vttu.coding_system_tt,
	vttu.comment_tt,
	vttu.code_unified,
	vttu.name_unified,
	vttu.coding_system_unified,
	vttu.comment_unified,
	-- management keys
	-- clin.clin_root_item
	tr.pk_item,
	tr.fk_encounter as pk_encounter,
	tr.fk_episode as pk_episode,
	-- test_result
	tr.fk_type as pk_test_type,
--	tr.fk_reviewer as pk_reviewer,
	tr.modified_when,
	tr.modified_by,
	tr.xmin as xmin_test_result,
	-- v_unified_test_types
	vttu.pk_test_org,
	vttu.pk_test_type_unified,
	-- v_pat_episodes
	vpe.pk_health_issue
from
	clin.test_result tr,
	clin.v_unified_test_types vttu,
	clin.v_pat_episodes vpe
where
	vttu.pk_test_type=tr.fk_type
		and
	tr.fk_episode=vpe.pk_episode
;

comment on view clin.v_test_results is
	'denormalized view over test_results joined with (possibly unified) test
	 type and patient/episode/encounter keys';


create view clin.v_lab_requests as
select
	vpi.pk_patient as pk_patient,
	lr.pk as pk_request,
	torg.internal_name as lab_name,
	lr.request_id as request_id,
	lr.lab_request_id as lab_request_id,
	lr.clin_when as sampled_when,
	lr.lab_rxd_when as lab_rxd_when,
	lr.results_reported_when as results_reported_when,
	lr.request_status as request_status,
	_(lr.request_status) as l10n_request_status,
	lr.is_pending as is_pending,
	lr.narrative as progress_note,
	lr.fk_test_org as pk_test_org,
	lr.fk_requestor as pk_requestor,
	lr.fk_encounter as pk_encounter,
	lr.fk_episode as pk_episode,
	vpi.pk_health_issue as pk_health_issue,
	lr.pk_item as pk_item,
	lr.modified_when as modified_when,
	lr.modified_by as modified_by,
	lr.soap_cat as soap_cat,
	lr.xmin as xmin_lab_request
from
	clin.lab_request lr,
	clin.test_org torg,
	clin.v_pat_items vpi
where
	lr.fk_test_org=torg.pk
		and
	vpi.pk_item = lr.pk_item
;

comment on view clin.v_lab_requests is
	'denormalizes lab requests per test organization';


create view clin.v_results4lab_req as
select
	vtr.pk_patient,
	vtr.pk_test_result as pk_result,
	lr.clin_when as req_when,			-- FIXME: should be sampled_when
	lr.lab_rxd_when,
	vtr.clin_when as val_when,
	lr.results_reported_when as reported_when,
	vtr.unified_code,
	vtr.unified_name,
	vtr.code_tt as lab_code,
	vtr.name_tt as lab_name,
	vtr.unified_val,
	vtr.val_num,
	vtr.val_alpha,
	vtr.val_unit,
	vtr.conversion_unit,
	vtr.soap_cat,
	vtr.comment as progress_note_result,
	coalesce(lr.narrative, '') as progress_note_request,
	vtr.val_normal_range,
	vtr.val_normal_min,
	vtr.val_normal_max,
	vtr.val_target_range,
	vtr.val_target_min,
	vtr.val_target_max,
	vtr.abnormality_indicator as abnormal,
	vtr.note_provider,
	lr.request_status as request_status,
	vtr.norm_ref_group as ref_group,
	lr.request_id,
	lr.lab_request_id,
	vtr.material,
	vtr.material_detail,
	vtr.pk_test_type,
	lr.pk as pk_request,
	lr.fk_test_org as pk_test_org,
	lr.fk_requestor as pk_requestor,
	vtr.pk_health_issue,
	vtr.pk_encounter,
	vtr.pk_episode,
	vtr.xmin_test_result as xmin_test_result
-- additional fields to carry over
--	, vtr.coding_system_tt,
--	vtr.comment_tt,
--	vtr.code_unified,
--	vtr.name_unified,
--	vtr.coding_system_unified,
--	vtr.comment_unified,
--	vtr.pk_test_org,
--	vtr.pk_test_type_unified,
from
	clin.v_test_results vtr,
	clin.lab_request lr,
	clin.lnk_result2lab_req lr2lr
where
	lr2lr.fk_result=vtr.pk_test_result
		and
	lr2lr.fk_request=lr.pk
;

comment on view clin.v_results4lab_req is
	'shows denormalized lab results per request';

-- ==========================================================
-- allergy stuff
drop view if exists clin.v_pat_allergies cascade;

create view clin.v_pat_allergies as
select
	a.id as pk_allergy,
	vpep.pk_patient as pk_patient,
	case when coalesce(trim(both from a.allergene), '') = ''
		then a.substance
		else a.allergene
	end as descriptor,
	a.allergene as allergene,
	a.substance as substance,
	a.substance_code as substance_code,
	a.generics as generics,
	a.generic_specific as generic_specific,
	a.atc_code as atc_code,
	at.value as type,
	_(at.value) as l10n_type,
	a.definite as definite,
	a.narrative as reaction,
	a.id_type as pk_type,
	a.pk_item as pk_item,
	a.clin_when as date,
	vpep.pk_health_issue as pk_health_issue,
	a.fk_episode as pk_episode,
	a.fk_encounter as pk_encounter,
	a.xmin as xmin_allergy,
	a.modified_when as modified_when,
	a.modified_by as modified_by
from
	clin.allergy a,
	clin._enum_allergy_type at,
	clin.v_pat_episodes vpep
where
	vpep.pk_episode=a.fk_episode
		and
	at.id=a.id_type
;

-- =============================================
-- coded narrative
drop index if exists clin.idx_coded_terms;
drop function if exists clin.add_coded_term(text, text, text) cascade;

create index idx_coded_terms on clin.coded_narrative(md5(term));

create function clin.add_coded_term(text, text, text) returns boolean as '
declare
	_term alias for $1;
	_code alias for $2;
	_system alias for $3;
	_tmp text;
begin
	select into _tmp ''1'' from clin.coded_narrative
		where term = _term and code = _code and xfk_coding_system = _system;
	if found then
		return True;
	end if;
	insert into clin.coded_narrative (term, code, xfk_coding_system)
		values (_term, _code, _system);
	return True;
end;' language 'plpgsql';

-- =============================================
-- diagnosis views

create view clin.v_pat_diag as
select
	vpi.pk_patient as pk_patient,
	cn.clin_when as diagnosed_when,
	cn.narrative as diagnosis,
	cd.laterality as laterality,
	cd.is_chronic as is_chronic,
	cd.is_active as is_active,
	cd.is_definite as is_definite,
	cd.clinically_relevant as clinically_relevant,
	cd.pk as pk_diag,
	cd.fk_narrative as pk_narrative,
	cn.fk_encounter as pk_encounter,
	cn.fk_episode as pk_episode,
	cd.xmin as xmin_clin_diag,
	cn.xmin as xmin_clin_narrative
from
	clin.clin_diag cd,
	clin.clin_narrative as cn,
	clin.v_pat_items vpi
where
	cn.soap_cat='a'
		and
	cd.fk_narrative = cn.pk
		and
	cn.pk_item = vpi.pk_item
;

comment on view clin.v_pat_diag is
	'denormalizing view over diagnoses per patient';

-- -----------------------
create view clin.v_codes4diag as
select distinct on (diagnosis, code, xfk_coding_system)
	con.term as diagnosis,
	con.code as code,
	con.xfk_coding_system as coding_system
from
	clin.coded_narrative con
where
	exists(select 1 from clin.v_pat_diag vpd where vpd.diagnosis = con.term)
;

comment on view clin.v_codes4diag is
	'a lookup view for all the codes associated with a
	 diagnosis, a diagnosis can appear several times,
	  namely once per associated code';

-- -----------------------------
create view clin.v_pat_narrative as
select
	vpi.pk_patient as pk_patient,
	cn.clin_when as date,
	case when ((select 1 from dem.v_staff where db_user = cn.modified_by) is null)
		then '<' || cn.modified_by || '>'
		else (select short_alias from dem.v_staff where db_user = cn.modified_by)
	end as provider,
	cn.soap_cat as soap_cat,
	cn.narrative as narrative,
	cn.pk_item as pk_item,
	cn.pk as pk_narrative,
	vpi.pk_health_issue as pk_health_issue,
	cn.fk_episode as pk_episode,
	cn.fk_encounter as pk_encounter,
	cn.xmin as xmin_clin_narrative
from
	clin.clin_narrative cn,
	clin.v_pat_items vpi
where
	cn.pk_item = vpi.pk_item
;

comment on view clin.v_pat_narrative is
	'patient narrative aggregated from all clin_root_item child tables;
	 the narrative is unprocessed and denormalized context using v_pat_items is added';

-- ---------------------------------------------
drop view if exists clin.v_pat_narrative_soap cascade;

create view clin.v_pat_narrative_soap as
SELECT
	vpep.pk_patient
		AS pk_patient,
	cn.clin_when
		AS date, 
	CASE WHEN (( SELECT 1 FROM dem.v_staff WHERE v_staff.db_user = cn.modified_by)) IS NULL
		THEN ('<'::text || cn.modified_by::text) || '>'::text
		ELSE (SELECT v_staff.short_alias FROM dem.v_staff WHERE v_staff.db_user = cn.modified_by)
	END AS provider,
	cn.soap_cat
		as soap_cat,
	cn.narrative
		as narrative,
	cn.pk_item
		as pk_item,
	cn.pk
		AS pk_narrative,
	vpep.pk_health_issue
		AS pk_health_issue,
	cn.fk_episode
		AS pk_episode,
	cn.fk_encounter
		AS pk_encounter,
	cn.xmin
		AS xmin_clin_narrative
FROM
	clin.clin_narrative cn,
	clin.v_pat_episodes vpep
WHERE
	vpep.pk_episode = cn.fk_episode
;

comment on view clin.v_pat_narrative_soap is
	'patient SOAP-only narrative;
	 this view aggregates all clin.clin_narrative rows
	 and adds denormalized context';

-- =============================================
-- types of clin.clin_root_item

-- ---------------------------------------------
-- custom referential integrity
drop function if exists f_rfi_type2item() cascade;

create function f_rfi_type2item() returns trigger as '
declare
	dummy integer;
	msg text;
begin
	-- does fk_item change at all ?
	if TG_OP = ''UPDATE'' then
		if NEW.fk_item = OLD.fk_item then
			return NEW;
		end if;
	end if;
	-- check referential integrity
	select into dummy 1 from clin.clin_root_item where pk_item=NEW.fk_item;
	if not found then
		msg := ''referential integrity violation: clin.lnk_type2item.fk_item ['' || NEW.fk_item || ''] not in <clin_root_item.pk_item>'';
		raise exception ''%'', msg;
		return NULL;
	end if;
	return NEW;
end;
' language 'plpgsql';

create trigger tr_rfi_type2item
	after insert or update
	on clin.lnk_type2item
	for each row
		execute procedure f_rfi_type2item()
;

comment on function f_rfi_type2item() is
	'function used to check referential integrity from
	 clin.lnk_type2item to clin.clin_root_item with a custom trigger';

--comment on trigger tr_rfi_type2item is
--	'trigger to check referential integrity from
--	 clin.lnk_type2item to clin.clin_root_item';

-- ---------------------------------------------
create view clin.v_pat_item_types as
select
	items.pk_item as pk_item,
	items.pk_patient as pk_patient,
	items.code as code,
	items.narrative as narrative,
	items.type as type
from
	((clin.v_pat_items vpi inner join clin.lnk_type2item lt2i on (vpi.pk_item=lt2i.fk_item)) lnkd_items
		inner join clin.clin_item_type cit on (lnkd_items.fk_type=cit.pk)) items
;

-- ---------------------------------------------
create view clin.v_types4item as
select distinct on (narrative, code, type, src_table)
	items.code as code,
	items.narrative as narrative,
	items.type as type,
	items.soap_cat as soap_cat,
	items.src_table as src_table
from
	((clin.v_pat_items vpi inner join clin.lnk_type2item lt2i on (vpi.pk_item=lt2i.fk_item)) lnkd_items
		inner join clin.clin_item_type cit on (lnkd_items.fk_type=cit.pk)) items
;

-- =============================================
-- family history

-- ---------------------------------------------
-- custom check constraint
-- FIXME: finish
--drop function if exists f_check_narrative_is_fHx();
--drop trigger if exists tr_check_narrative_is_fHx;

--create function f_check_narrative_is_fHx() returns trigger as '
--declare
--	item_pk integer;
--	msg text;
--begin
--	-- does fk_narrative change at all ?
--	if TG_OP = ''UPDATE'' then
--		if NEW.fk_narrative = OLD.fk_narrative then
--			return NEW;
--		end if;
--	end if;
--	-- is it typed fHx ?
--	select into item_pk 1 from v_pat_item_types vpit
--	where
--		vpit.pk_item = NEW.pk_item
	
	
--	 lnk_type2item
--	where
--		fk_item = (select pk_item from clin.clin_narrative where pk=NEW.fk_narrative)
--			and
--		fk_type = (select pk from clin.clin_item_type )
--	;
--	if not found then
--		msg := ''referential integrity violation: clin.lnk_type2item.fk_item ['' || NEW.fk_item || ''] not in <clin_root_item.pk_item>'';
--		raise exception ''%'', msg;
--		return NULL;
--	end if;
--	return NEW;
--end;
-- ' language 'plpgsql';

-- create trigger tr_rfi_type2item
--	after insert or update
--	on clin.lnk_type2item
--	for each row
--		execute procedure f_rfi_type2item()
--;

-- comment on function f_rfi_type2item() is
--	'function used to check referential integrity from
--	 clin.lnk_type2item to clin.clin_root_item with a custom trigger';

-- comment on trigger tr_rfi_type2item is
--	'trigger to check referential integrity from
--	 lnk_type2item to clin.clin_root_item';

create view clin.v_hx_family as
-- those not linked to another patient as relative
select
	vpi.pk_patient as pk_patient,
	vpi.pk_health_issue as pk_health_issue,

	chxf.clin_when as clin_when,
	chxf.modified_when as modified_when,
	chxf.modified_by as modified_by,
	chxf.fk_encounter as pk_encounter,
	chxf.fk_episode as pk_episode,
	chxf.narrative as relationship,
	chxf.soap_cat as soap_cat,
	chxf.pk as pk_clin_hx_family,
	chxf.fk_hx_family_item as pk_hx_family_item,

	null::integer as pk_narrative_condition,
	null::integer as pk_relative_identity,
	hxfi.name_relative as name_relative,
	hxfi.dob_relative as dob_relative,
	hxfi.condition as condition,
	hxfi.age_noted as age_noted,
	hxfi.age_of_death as age_of_death,
	hxfi.is_cause_of_death as is_cause_of_death
from
	clin.v_pat_items vpi,
	clin.clin_hx_family chxf,
	clin.hx_family_item hxfi
where
	vpi.pk_item = chxf.pk_item
		and
	hxfi.pk = chxf.fk_hx_family_item
		and
	hxfi.fk_narrative_condition is null
		and
	hxfi.fk_relative is null

UNION

-- those linked to another patient as relative
select
	vpi.pk_patient as pk_patient,
	vpi.pk_health_issue as pk_health_issue,

	chxf.clin_when as clin_when,
	chxf.modified_when as modified_when,
	chxf.modified_by as modified_by,
	chxf.fk_encounter as pk_encounter,
	chxf.fk_episode as pk_episode,
	chxf.narrative as relationship,
	chxf.soap_cat as soap_cat,
	chxf.pk as pk_clin_hx_family,
	chxf.fk_hx_family_item as pk_hx_family_item,

	null::integer as pk_narrative_condition,
	hxfi.fk_relative as pk_relative_identity,
	vbp.firstnames || ' ' || vbp.lastnames as name_relative,
	vbp.dob as dob_relative,
	hxfi.condition as condition,
	hxfi.age_noted as age_noted,
	hxfi.age_of_death as age_of_death,
	hxfi.is_cause_of_death as is_cause_of_death
from
	clin.v_pat_items vpi,
	clin.clin_hx_family chxf,
	clin.hx_family_item hxfi,
	dem.v_basic_person vbp
where
	vpi.pk_item = chxf.pk_item
		and
	hxfi.pk = chxf.fk_hx_family_item
		and
	hxfi.fk_narrative_condition is null
		and
	hxfi.fk_relative = vbp.pk_identity

UNION

-- those linked to a condition of another patient being a relative
select
	vpn.pk_patient as pk_patient,
	vpn.pk_health_issue as pk_health_issue,

	chxf.clin_when as clin_when,
	chxf.modified_when as modified_when,
	chxf.modified_by as modified_by,
	chxf.fk_encounter as pk_encounter,
	chxf.fk_episode as pk_episode,
	chxf.narrative as relationship,
	chxf.soap_cat as soap_cat,
	chxf.pk as pk_clin_hx_family,
	chxf.fk_hx_family_item as pk_hx_family_item,

	hxfi.fk_narrative_condition as pk_narrative_condition,
	vpn.pk_patient as pk_relative_identity,
	vbp.firstnames || ' ' || vbp.lastnames as name_relative,
	vbp.dob as dob_relative,
	vpn.narrative as condition,
	hxfi.age_noted as age_noted,
	hxfi.age_of_death as age_of_death,
	hxfi.is_cause_of_death as is_cause_of_death
from
	clin.clin_hx_family chxf,
	clin.hx_family_item hxfi,
	dem.v_basic_person vbp,
	clin.v_pat_narrative vpn
where
	hxfi.pk = chxf.fk_hx_family_item
		and
	hxfi.fk_narrative_condition = vpn.pk_narrative
		and
	hxfi.fk_relative is null
		and
	vbp.pk_identity = vpn.pk_patient
;


-- =============================================
-- problem list

drop view if exists clin.v_problem_list cascade;

create view clin.v_problem_list as
select	-- all the (open) episodes
	vpep.pk_patient as pk_patient,
	vpep.description as problem,
	'episode' as type,
	_('episode') as l10n_type,
	'true'::boolean as problem_active,
	'true'::boolean as clinically_relevant,
	vpep.pk_episode as pk_episode,
	vpep.pk_health_issue as pk_health_issue
from
	clin.v_pat_episodes vpep
where
	vpep.episode_open is true

union	-- and

select	-- all the (clinically relevant) health issues
	chi.id_patient as pk_patient,
	chi.description as problem,
	'issue' as type,
	_('health issue') as l10n_type,
	chi.is_active as problem_active,
	'true'::boolean as clinically_relevant,
	null as pk_episode,
	chi.pk as pk_health_issue
from
	clin.health_issue chi
where
	chi.clinically_relevant is true
;

-- =============================================
-- *complete* narrative for searching

-- FIXME: add form_data, fk_encounter, fk_health_issue, fk_episode etc
create view clin.v_narrative4search as
-- clin.clin_root_items
select
	vpi.pk_patient as pk_patient,
	vpi.soap_cat as soap_cat,
	vpi.narrative as narrative,
	vpi.pk_item as src_pk,
	vpi.src_table as src_table
from
	clin.v_pat_items vpi
where
	trim(coalesce(vpi.narrative, '')) != ''

union	-- health issues
select
	chi.id_patient as pk_patient,
	'a' as soap_cat,
	chi.description as narrative,
	chi.pk as src_pk,
	'clin.health_issue' as src_table
from
	clin.health_issue chi
where
	trim(coalesce(chi.description, '')) != ''

union	-- encounters
select
	cenc.fk_patient as pk_patient,
	's' as soap_cat,
	cenc.reason_for_encounter || '; ' || cenc.assessment_of_encounter as narrative,
	cenc.pk as src_pk,
	'clin.encounter' as src_table
from
	clin.encounter cenc

union	-- episodes
select
	vpep.pk_patient as pk_patient,
	's' as soap_cat,
	vpep.description as narrative,
	vpep.pk_episode as src_pk,
	'clin.episode' as src_table
from
	clin.v_pat_episodes vpep

union	-- family history
select
	vhxf.pk_patient as pk_patient,
	vhxf.soap_cat as soap_cat,
	vhxf.relationship || ' ('
		|| vhxf.name_relative || ') @ '
		|| vhxf.age_noted || ': '
		|| vhxf.condition
	as narrative,
	vhxf.pk_hx_family_item as src_pk,
	'clin.hx_family_item' as src_table
from
	clin.v_hx_family vhxf

;

comment on view clin.v_narrative4search is
	'unformatted *complete* narrative for patients
	 including health issue/episode/encounter descriptions,
	 mainly for searching the narrative';


-- =============================================
-- complete narrative for display as a journal

create view clin.v_emr_journal as

-- clin.clin_narrative
select
	vpi.pk_patient as pk_patient,
	cn.modified_when as modified_when,
	cn.clin_when as clin_when,
	case when ((select 1 from dem.v_staff where db_user = cn.modified_by) is null)
		then '<' || cn.modified_by || '>'
		else (select short_alias from dem.v_staff where db_user = cn.modified_by)
	end as modified_by,
	cn.soap_cat as soap_cat,
	cn.narrative,
	cn.fk_encounter as pk_encounter,
	cn.fk_episode as pk_episode,
	vpi.pk_health_issue as pk_health_issue,
	cn.pk as src_pk,
	'clin.clin_narrative'::text as src_table
from
	clin.v_pat_items vpi,
	clin.clin_narrative cn
where
	vpi.pk_item = cn.pk_item

union	-- health issues
select
	chi.id_patient as pk_patient,
	chi.modified_when as modified_when,
	chi.modified_when as clin_when,
	case when ((select 1 from dem.v_staff where db_user = chi.modified_by) is null)
		then '<' || chi.modified_by || '>'
		else (select short_alias from dem.v_staff where db_user = chi.modified_by)
	end as modified_by,
	'a' as soap_cat,
	_('health issue') || ': ' || chi.description || '; '
		|| _('noted at age') || ': ' || coalesce(chi.age_noted::text, '?') || ';'
	as narrative,
	-1 as pk_encounter,
	-1 as pk_episode,
	chi.pk as pk_health_issue,
	chi.pk as src_pk,
	'clin.health_issue'::text as src_table
from
	clin.health_issue chi

union	-- encounters
select
	cenc.fk_patient as pk_patient,
	cenc.modified_when as modified_when,
	-- FIXME: or last_affirmed ?
	cenc.started as clin_when,
	case when ((select 1 from dem.v_staff where db_user = cenc.modified_by) is null)
		then '<' || cenc.modified_by || '>'
		else (select short_alias from dem.v_staff where db_user = cenc.modified_by)
	end as modified_by,
	's' as soap_cat,
	_('encounter') || ': ' || _('RFE') || ': ' || cenc.reason_for_encounter || '; ' || _('AOE') || ':' as narrative,
	cenc.pk as pk_encounter,
	-1 as pk_episode,
	-1 as pk_health_issue,
	cenc.pk as src_pk,
	'clin.encounter'::text as src_table
from
	clin.encounter cenc

union	-- episodes
select
	vpep.pk_patient as pk_patient,
	vpep.episode_modified_when as modified_when,
	vpep.episode_modified_when as clin_when,
	case when ((select 1 from dem.v_staff where db_user = vpep.episode_modified_by) is null)
		then '<' || vpep.episode_modified_by || '>'
		else (select short_alias from dem.v_staff where db_user = vpep.episode_modified_by)
	end as modified_by,
	's' as soap_cat,
	_('episode') || ': ' || vpep.description as narrative,
	-1 as pk_encounter,
	vpep.pk_episode as pk_episode,
	-1 as pk_health_issue,
	vpep.pk_episode as src_pk,
	'clin.episode'::text as src_table
from
	clin.v_pat_episodes vpep

union	-- family history
select
	vhxf.pk_patient as pk_patient,
	vhxf.modified_when as modified_when,
	vhxf.clin_when as clin_when,
	case when ((select 1 from dem.v_staff where db_user = vhxf.modified_by) is null)
		then '<' || vhxf.modified_by || '>'
		else (select short_alias from dem.v_staff where db_user = vhxf.modified_by)
	end as modified_by,
	vhxf.soap_cat as soap_cat,
	_(vhxf.relationship) || ' '
		|| vhxf.name_relative || ' @ '
		|| vhxf.age_noted || ': '
		|| vhxf.condition
	as narrative,
	vhxf.pk_encounter as pk_encounter,
	vhxf.pk_episode as pk_episode,
	vhxf.pk_health_issue as pk_health_issue,
	vhxf.pk_hx_family_item as src_pk,
	'clin.hx_family_item'::text as src_table
from
	clin.v_hx_family vhxf

union	-- vaccinations
select
	vpv4i.pk_patient as pk_patient,
	vpv4i.modified_when as modified_when,
	vpv4i.date as clin_when,
	case when ((select 1 from dem.v_staff where db_user = vpv4i.modified_by) is null)
		then '<' || vpv4i.modified_by || '>'
		else (select short_alias from dem.v_staff where db_user = vpv4i.modified_by)
	end as modified_by,
	'p' as soap_cat,
	_('vaccine') || ': ' || vpv4i.vaccine || '; '
		|| _('batch no') || ': ' || vpv4i.batch_no || '; '
		|| _('indication') || ': ' || vpv4i.l10n_indication || '; '
		|| _('site') || ': ' || vpv4i.site || '; '
		|| _('notes') || ': ' || vpv4i.narrative || ';'
	as narrative,
	vpv4i.pk_encounter as pk_encounter,
	vpv4i.pk_episode as pk_episode,
	vpv4i.pk_health_issue as pk_health_issue,
	vpv4i.pk_vaccination as src_pk,
	'vaccination'::text as src_table
from
	clin.v_pat_vaccinations4indication vpv4i

union -- allergies
select
	vpa.pk_patient as pk_patient,
	vpa.modified_when as modified_when,
	vpa.date as clin_when,
	case when ((select 1 from dem.v_staff where db_user = vpa.modified_by) is null)
		then '<' || vpa.modified_by || '>'
		else (select short_alias from dem.v_staff where db_user = vpa.modified_by)
	end as modified_by,
	's' as soap_cat,	-- FIXME: pull in proper soap_cat
	_('allergene') || ': ' || coalesce(vpa.allergene, '') || '; '
		|| _('substance') || ': ' || vpa.substance || '; '
		|| _('generic')   || ': ' || coalesce(vpa.generics, '') || '; '
		|| _('ATC code')  || ': ' || coalesce(vpa.atc_code, '') || '; '
		|| _('type')      || ': ' || vpa.l10n_type || '; '
		|| _('reaction')  || ': ' || coalesce(vpa.reaction, '') || ';'
	as narrative,
	vpa.pk_encounter as pk_encounter,
	vpa.pk_episode as pk_episode,
	vpa.pk_health_issue as pk_health_issue,
	vpa.pk_allergy as src_pk,
	'clin.allergy' as src_table
from
	clin.v_pat_allergies vpa

union	-- lab requests
select
	vlr.pk_patient as pk_patient,
	vlr.modified_when as modified_when,
	vlr.sampled_when as clin_when,
	case when ((select 1 from dem.v_staff where db_user = vlr.modified_by) is null)
		then '<' || vlr.modified_by || '>'
		else (select short_alias from dem.v_staff where db_user = vlr.modified_by)
	end as modified_by,
	vlr.soap_cat as soap_cat,
	_('lab') || ': ' || vlr.lab_name || '; '
		|| _('sample ID') || ': ' || vlr.request_id || '; '
		|| _('sample taken') || ': ' || vlr.sampled_when || '; '
		|| _('status') || ': ' || vlr.l10n_request_status || '; '
		|| _('notes') || ': ' || coalesce(vlr.progress_note, '') || ';'
	as narrative,
	vlr.pk_encounter as pk_encounter,
	vlr.pk_episode as pk_epiode,
	vlr.pk_health_issue as pk_health_issue,
	vlr.pk_item as src_pk,
	'lab_request' as src_table
from
	clin.v_lab_requests vlr

union	-- test results
select
	vtr.pk_patient as pk_patient,
	vtr.modified_when as modified_when,
	vtr.clin_when as clin_when,
	case when ((select 1 from dem.v_staff where db_user = vtr.modified_by) is null)
		then '<' || vtr.modified_by || '>'
		else (select short_alias from dem.v_staff where db_user = vtr.modified_by)
	end as modified_by,
	vtr.soap_cat as soap_cat,
	_('code') || ': ' || vtr.unified_code || '; '
		|| _('name') || ': ' || vtr.unified_name || '; '
		|| _('value') || ': ' || vtr.unified_val || ' ' || vtr.val_unit || ' ('
--		|| coalesce(vtr.unified_target_min, -9999)::text || ' - '
--		|| coalesce(vtr.unified_target_max, -9999)::text || ' / '
		|| coalesce(vtr.unified_target_range, '?') || '); '
		|| _('notes') || vtr.comment || ';'
	as narrative,
	vtr.pk_encounter as pk_encounter,
	vtr.pk_episode as pk_episode,
	vtr.pk_health_issue as pk_health_issue,
	vtr.pk_test_result as src_pk,
	'test_result' as src_table
from
	clin.v_test_results vtr
;

comment on view clin.v_emr_journal is
	'patient narrative including health issue/episode/
	 encounter descriptions, mainly for display as a journal';

-- =============================================
-- a waiting list
drop view if exists clin.v_waiting_list cascade;

create view clin.v_waiting_list as
select
	wl.list_position as list_position,
	wl.urgency as urgency,
	i.title as title,
	n.firstnames as firstnames,
	n.lastnames as lastnames,
	n.preferred as preferred_name,
	i.dob as dob,
	i.gender as gender,
	_(i.gender) as l10n_gender,
	wl.registered as registered,
	vmre.started as start_most_recent_encounter,
	vmre.reason_for_encounter as most_recent_rfe,
	wl.comment as comment,
	(select started from clin.encounter ce
	 where vmre.pk_encounter = ce.pk
	 order by last_affirmed desc limit 1 offset 1
	) as start_previous_encounter,
	i.pk as pk_identity,
	n.id as pk_name,
	i.pupic as pupic
from
	clin.waiting_list wl,
	dem.identity i,
	dem.names n,
	clin.v_most_recent_encounters vmre
where
	wl.fk_patient = i.pk and
	wl.fk_patient = n.id_identity and
	wl.fk_patient = vmre.pk_patient and
	i.deceased is NULL and
	n.active is true
;

-- =============================================
-- tables
GRANT SELECT, INSERT, UPDATE, DELETE ON
	clin.clin_root_item
	, clin.clin_root_item_pk_item_seq
	, clin.clin_item_type
	, clin.clin_item_type_pk_seq
	, clin.lnk_type2item
	, clin.lnk_type2item_pk_seq
	, clin.clin_narrative
	, clin.clin_narrative_pk_seq
	, clin.coded_narrative
	, clin.coded_narrative_pk_seq
	, clin.clin_hx_family
	, clin.clin_hx_family_pk_seq
	, clin.hx_family_item
	, clin.hx_family_item_pk_seq
	, clin.clin_diag
	, clin.clin_diag_pk_seq
	, clin.clin_aux_note
	, clin.clin_aux_note_pk_seq
	, clin._enum_allergy_type
	, clin._enum_allergy_type_id_seq
	, clin.allergy
	, clin.allergy_id_seq
	, clin.allergy_state
	, clin.allergy_state_id_seq
	, clin.xlnk_identity
	, clin.xlnk_identity_pk_seq
	, clin.form_instances
	, clin.form_instances_pk_seq
	, clin.form_data
	, clin.form_data_pk_seq
	, clin.clin_medication
	, clin.clin_medication_pk_seq
	, clin.soap_cat_ranks
	, clin.waiting_list
	, clin.waiting_list_pk_seq
TO GROUP "gm-doctors";

-- measurements
grant select, insert, update, delete on
	clin.test_org
	, clin.test_org_pk_seq
	, clin.test_type
	, clin.test_type_pk_seq
	, clin.test_type_unified
	, clin.test_type_unified_pk_seq
	, clin.lnk_ttype2unified_type
	, clin.lnk_ttype2unified_type_pk_seq
	, clin.lnk_tst2norm
	, clin.lnk_tst2norm_id_seq
	, clin.test_result
	, clin.test_result_pk_seq
	, clin.lab_request
	, clin.lab_request_pk_seq
	, clin.lnk_result2lab_req
	, clin.lnk_result2lab_req_pk_seq
	, clin.reviewed_test_results
to group "gm-doctors";

-- views
grant select on
	clin.v_pat_narrative
	, clin.v_pat_items
	, clin.v_pat_allergies
	, clin.v_test_type_unified
	, clin.v_unified_test_types
	, clin.v_test_results
	, clin.v_lab_requests
	, clin.v_results4lab_req
	, clin.v_test_org_profile
	, clin.v_pat_diag
	, clin.v_codes4diag
	, clin.v_pat_item_types
	, clin.v_types4item
	, clin.v_problem_list
	, clin.v_narrative4search
	, clin.v_emr_journal
	, clin.v_hx_family
	, clin.v_waiting_list
to group "gm-doctors";

-- =============================================
select log_script_insertion('$RCSfile: gmClinicalViews.sql,v $', '$Revision: 1.184 $');
