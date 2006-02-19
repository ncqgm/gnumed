-- project: GnuMed

-- purpose: views for easier clinical data access
-- author: Karsten Hilbert
-- license: GPL (details at http://gnu.org)

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmClinicalViews.sql,v $
-- $Id: gmClinicalViews.sql,v 1.173 2006-02-19 13:45:05 ncq Exp $

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
	'stores family history items independant of the patient,
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
	 may or may not be an opaque value as regards GnuMed';
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
\unset ON_ERROR_STOP
drop index clin.idx_cri_encounter;
drop index clin.idx_cri_episode;

drop index clin.idx_clnarr_encounter;
drop index clin.idx_clnarr_episode;

drop index clin.idx_clanote_encounter;
drop index clin.idx_clanote_episode;

drop index clin.idx_vacc_encounter;
drop index clin.idx_vacc_episode;

drop index clin.idx_allg_encounter;
drop index clin.idx_allg_episode;

drop index clin.idx_formi_encounter;
drop index clin.idx_formi_episode;

drop index clin.idx_cmeds_encounter;
drop index clin.idx_cmeds_episode;

drop index clin.idx_ref_encounter;
drop index clin.idx_ref_episode;

drop index clin.idx_tres_encounter;
drop index clin.idx_tres_episode;

drop index clin.idx_lreq_encounter;
drop index clin.idx_lreq_episode;

\set ON_ERROR_STOP 1

-- clin.clin_root_item & children indices
create index idx_cri_encounter on clin.clin_root_item(fk_encounter);
create index idx_cri_episode on clin.clin_root_item(fk_episode);

create index idx_clnarr_encounter on clin.clin_narrative(fk_encounter);
create index idx_clnarr_episode on clin.clin_narrative(fk_episode);

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
\unset ON_ERROR_STOP

drop index clin.idx_narr_soap;
drop index clin.idx_narr_s;
drop index clin.idx_narr_o;
drop index clin.idx_narr_a;
drop index clin.idx_narr_p;

create index idx_narr_s on clin.clin_narrative(soap_cat) where soap_cat='s';
create index idx_narr_o on clin.clin_narrative(soap_cat) where soap_cat='o';
create index idx_narr_a on clin.clin_narrative(soap_cat) where soap_cat='a';
create index idx_narr_p on clin.clin_narrative(soap_cat) where soap_cat='p';

\set ON_ERROR_STOP 1

create index idx_narr_soap on clin.clin_narrative(soap_cat);

-- clin.clin_medication
\unset ON_ERROR_STOP
drop index clin.idx_clin_medication;
create index idx_clin_medication on clin.clin_medication(discontinued) where discontinued is not null;
\set ON_ERROR_STOP 1

-- =============================================
-- clin_root_item stuff
\unset ON_ERROR_STOP
drop function clin.f_announce_clin_item_mod() cascade;
\set ON_ERROR_STOP 1

create function clin.f_announce_clin_item_mod() returns opaque as '
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
\unset ON_ERROR_STOP
drop function clin.f_protect_clin_root_item() cascade;
\set ON_ERROR_STOP 1

create function clin.f_protect_clin_root_item() returns opaque as '
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
create view clin.v_pat_items as
select
	extract(epoch from cri.clin_when) as age,
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
order by
	age
;

-- ==========================================================
-- measurements stuff

\unset ON_ERROR_STOP
drop view clin.v_test_type_unified cascade;
\set ON_ERROR_STOP 1

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
\unset ON_ERROR_STOP
drop index clin.idx_coded_terms;
drop function clin.add_coded_term(text, text, text) cascade;
\set ON_ERROR_STOP 1

create index idx_coded_terms on clin.coded_narrative(term);

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
	'patient SOAP narrative;
	 this view aggregates all clin.clin_narrative rows
	 and adds denormalized context';

-- =============================================
-- types of clin.clin_root_item

-- ---------------------------------------------
-- custom referential integrity
\unset ON_ERROR_STOP
drop function f_rfi_type2item() cascade;
\set ON_ERROR_STOP 1

create function f_rfi_type2item() returns opaque as '
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
--\unset ON_ERROR_STOP
--drop function f_check_narrative_is_fHx();
--drop trigger tr_check_narrative_is_fHx;
--\set ON_ERROR_STOP 1

--create function f_check_narrative_is_fHx() returns opaque as '
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
	cenc.rfe || '; ' || cenc.aoe as narrative,
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
	_('encounter') || ': ' || _('RFE') || ': ' || cenc.rfe || '; ' || _('AOE') || ':' as narrative,
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
	clin.v_pat_vacc4ind vpv4i

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

\unset ON_ERROR_STOP
drop view clin.v_waiting_list cascade;
\set ON_ERROR_STOP 1

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
	vmre.rfe as most_recent_rfe,
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
-- do simple schema revision tracking
\unset ON_ERROR_STOP
delete from gm_schema_revision where filename='$RCSfile: gmClinicalViews.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmClinicalViews.sql,v $', '$Revision: 1.173 $');

-- =============================================
-- $Log: gmClinicalViews.sql,v $
-- Revision 1.173  2006-02-19 13:45:05  ncq
-- - move the rest of the dynamic vacc stuff from gmClinicalViews.sql
--   into gmClin-Vaccination-dynamic.sql
-- - add vaccination schedule constraint enumeration data
-- - add is_active to clin.vacc_regime
-- - add clin.vacc_regime_constraint
-- - add clin.lnk_constraint2vacc_reg
-- - proper grants
--
-- Revision 1.172  2006/02/10 14:08:58  ncq
-- - factor out EMR structure clinical schema into its own set of files
--
-- Revision 1.171  2006/02/08 15:15:39  ncq
-- - factor our vaccination stuff into its own set of files
-- - remove clin.lnk_vacc_ind2code in favour of clin.coded_term usage
-- - improve comments as discussed on the list
--
-- Revision 1.170  2006/01/27 22:24:45  ncq
-- - move reviewed_test_results here
--
-- Revision 1.169  2006/01/23 22:10:57  ncq
-- - staff.sign -> .short_alias
--
-- Revision 1.168  2006/01/10 23:22:17  sjtan
--
-- update permissions for views
--
-- Revision 1.167  2006/01/06 10:12:02  ncq
-- - add missing grants
-- - add_table_for_audit() now in "audit" schema
-- - demographics now in "dem" schema
-- - add view v_inds4vaccine
-- - move staff_role from clinical into demographics
-- - put add_coded_term() into "clin" schema
-- - put German things into "de_de" schema
--
-- Revision 1.166  2006/01/05 16:04:37  ncq
-- - move auditing to its own schema "audit"
--
-- Revision 1.165  2006/01/01 20:41:06  ncq
-- - move vacc_def constraints around
-- - add trigger constraint to make sure there's always base
--   immunization definitions for boosters
--
-- Revision 1.164  2005/12/29 21:48:09  ncq
-- - clin.vaccine.id -> pk
-- - remove clin.vaccine.last_batch_no
-- - add clin.vaccine_batches
-- - adjust test data and country data
--
-- Revision 1.163  2005/12/07 16:28:18  ncq
-- - with the help of the postgresql list fix the "add missing from"
--   error in v_hx_family
--
-- Revision 1.162  2005/12/06 13:26:55  ncq
-- - clin.clin_encounter -> clin.encounter
-- - also id -> pk
--
-- Revision 1.161  2005/12/05 19:05:59  ncq
-- - clin_episode -> episode
--
-- Revision 1.160  2005/12/04 09:42:06  ncq
-- - clin.clin_health_issue -> clin.health_issue
-- - properly use new add_table_for_notifies()
--
-- Revision 1.159  2005/11/29 19:06:13  ncq
-- - explicitely delete public.* tables from notify table and re-insert
--   clin.* tables since add_table_for_notifies doesn't support schema yet
--
-- Revision 1.158  2005/11/27 12:59:09  ncq
-- - comment out referral/constituent for now
--
-- Revision 1.157  2005/11/25 15:07:28  ncq
-- - create schema "clin" and move all things clinical into it
--
-- Revision 1.156  2005/10/26 21:33:25  ncq
-- - review status tracking
--
-- Revision 1.155  2005/09/25 17:49:24  ncq
-- - add start of current/previous encounter to waiting list view
--
-- Revision 1.154  2005/09/24 09:07:02  ncq
-- - removed left-over reference to clin_encounter.fk_provider
--
-- Revision 1.153  2005/09/22 15:43:48  ncq
-- - remove clin_encounter.fk_provider
-- - add v_waiting_list
--
-- Revision 1.152  2005/09/21 10:20:51  ncq
-- - waiting list grants
--
-- Revision 1.151  2005/09/19 16:19:58  ncq
-- - cleanup
-- - support rfe/aoe in clin_encounter and adjust to that
--
-- Revision 1.150  2005/09/13 11:56:20  ncq
-- - cleanup/comments
--
-- Revision 1.149  2005/09/11 17:41:20  ncq
-- - cleanup
-- - display provider sign in v_pat_narrative, not db account
--
-- Revision 1.148  2005/09/08 17:02:37  ncq
-- - include provider in v_pat_narrative
--
-- Revision 1.147  2005/08/15 16:30:42  ncq
-- - cleanup
-- - enforce "only one open episode per health issue at any time"
--
-- Revision 1.146  2005/07/14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.145  2005/06/19 13:36:10  ncq
-- - allow updating clin_root_item directly as Syan showed it to be working
-- - fix problem list to only include real problems
--
-- Revision 1.144  2005/06/01 23:18:48  ncq
-- - missing grants on hx_family_item
--
-- Revision 1.143  2005/05/17 08:17:04  ncq
-- - refine clin_narrative row mapping in v_emr_journal to display is_rfe status
--
-- Revision 1.142  2005/04/27 20:00:11  ncq
-- - add missing coalesce in v_emr_journal
--
-- Revision 1.141  2005/04/17 16:33:49  ncq
-- - improve clin_health_issue display in v_emr_journal
--
-- Revision 1.140  2005/04/12 10:08:34  ncq
-- - fix faulty index drop
-- - add l10n_type to v_problem_list
--
-- Revision 1.139  2005/04/08 09:59:34  ncq
-- - dramatically speed up (read: make usable) v_most_recent_encounters
-- - add three indices on clin_encounter for v_most_recent_encounters
-- - index on coded_narrative
-- - function add_coded_term()
-- - rewrite diagnosis views based on coded_narrative
--
-- Revision 1.138  2005/04/03 20:14:04  ncq
-- - soap_cat_ranks grant
--
-- Revision 1.137  2005/03/31 18:02:35  ncq
-- - move strings to data
--
-- Revision 1.136  2005/03/31 17:46:00  ncq
-- - cleanup, remove dead code
-- - add v_emr_journal
-- - enhance several views to include modified_when/modified_by for v_emr_journal
-- - improve v_pat_narrative
-- - v_compl_narrative -> v_narrative4search
-- - grants
--
-- Revision 1.135  2005/03/21 20:10:20  ncq
-- - v_patient_items -> v_pat_items for consistency
-- - add v_hx_family and include in v_compl_narrative
--
-- Revision 1.134  2005/03/20 18:07:47  ncq
-- - properly protect clin_root_item and be verbose about it
-- - v_hx_family needs to be rewritten
--
-- Revision 1.133  2005/03/14 17:47:55  ncq
-- - store time zone of insert into clin_encounter as a
--   reasonable approximation for other timestamp time zones
--
-- Revision 1.132  2005/03/14 15:16:04  ncq
-- - missing variable declaration in f_rfi_type2item
--
-- Revision 1.131  2005/03/14 14:45:40  ncq
-- - episode naming much simplified hence simplified views
-- - add episode name into v_compl_narrative
-- - some id_patient -> pk_patient
-- - v_hx_family and grants
-- - apparently lnk_type2item cannot foreign key its fk_item to
--   clin_root_item and expect to work with *child* tables of
--   clin_root_item :-(  so add custom referential integrity trigger,
--   this lacks on update/delete support, though, naturally
--
-- Revision 1.130  2005/03/11 22:55:50  ncq
-- - cleanup
-- - carry over provider into narrative view
--
-- Revision 1.129  2005/03/01 20:40:10  ncq
-- - require name for all episodes thereby fixing not being able to
--   refetch unnamed episodes in the Python middleware
--
-- Revision 1.128  2005/02/15 18:26:41  ncq
-- - test_result.id -> pk
--
-- Revision 1.127  2005/02/12 13:49:14  ncq
-- - identity.id -> identity.pk
-- - allow NULL for identity.fk_marital_status
-- - subsequent schema changes
--
-- Revision 1.126  2005/02/07 13:02:41  ncq
-- - v_test_type_local -> v_test_type_unified
-- - old v_test_type_unified -> v_unified_test_types
-- - follow-on changes, grants
-- - remove cruft
--
-- Revision 1.125  2005/01/31 20:16:39  ncq
-- - clin_episode has fk_patient, not id_patient
--
-- Revision 1.124  2005/01/31 19:49:39  ncq
-- - clin_health_issue does not yet follow primary key == pk
--
-- Revision 1.123  2005/01/31 19:42:53  ncq
-- - add 2 missing "end if;"
--
-- Revision 1.122  2005/01/31 19:12:26  ncq
-- - add trigger to announce episode changes
--
-- Revision 1.121  2005/01/24 17:57:43  ncq
-- - cleanup
-- - Ian's enhancements to address and forms tables
--
-- Revision 1.120  2004/12/15 10:48:32  ncq
-- - carry pk of narrative in episode views so business objects can
--   update it (eg rename the episode)
--
-- Revision 1.119  2004/12/14 20:06:59  ncq
-- - v_test_results.unified_target_* from val_target_* first or val_normal_* second
--
-- Revision 1.118  2004/12/06 21:09:38  ncq
-- - eventually properly implement episode naming via deferred constraint trigger
--
-- Revision 1.117  2004/11/28 14:37:00  ncq
-- - adjust to clin_episode.fk_clin_narrative instead of clin_narrative.is_episode_name
--
-- Revision 1.116  2004/11/26 13:51:18  ncq
-- - always hard to get quoting right for dynamic pl/pgsql
--
-- Revision 1.115  2004/11/26 12:18:04  ncq
-- - trigger/func _name_new_episode
--
-- Revision 1.114  2004/11/24 15:39:33  ncq
-- - clin_episode does not have clinically_relevant anymore as per discussion on list
--
-- Revision 1.113  2004/11/21 21:38:31  ncq
-- - fix chi.is_open to be is_active
--
-- Revision 1.112  2004/11/21 21:02:48  ncq
-- - episode: is_active -> is_open
--
-- Revision 1.111  2004/11/16 19:01:27  ncq
-- - adjust to episode name now living in clin_narrative
-- - v_named_episodes still needs work to properly account for
--   erronously unnamed episodes
--
-- Revision 1.110  2004/10/29 22:37:02  ncq
-- - propagate xmin to the relevant views to business classes can
--   use it for concurrency conflict detection
-- - fix v_problem_list to properly display a patient's problems
--
-- Revision 1.109  2004/10/12 09:50:21  ncq
-- - enhance v_vacc_regimes -> add "shots" field holding number of shots for regime
--
-- Revision 1.108  2004/10/11 19:32:19  ncq
-- - clean up v_pat_allergies
--
-- Revision 1.107  2004/09/29 19:17:24  ncq
-- - fix typos and grants
--
-- Revision 1.106  2004/09/29 10:38:22  ncq
-- - measurement views rewritten to match current discussion
--
-- Revision 1.105  2004/09/28 12:29:29  ncq
-- - add pk_vacc_def to v_vaccs_scheduled4pat
--
-- Revision 1.104  2004/09/25 13:25:56  ncq
-- - is_significant -> clinically_relevant
--
-- Revision 1.103  2004/09/22 14:12:19  ncq
-- - add rules to protect clin_root_item from direct insert/update/delete,
--   this prevents child table coherency issues
--
-- Revision 1.102  2004/09/20 21:14:11  ncq
-- - remove cruft, fix grants
-- - retire lnk_vacc2vacc_def for now as we seem to not need it
--
-- Revision 1.101  2004/09/18 13:49:32  ncq
-- - fix missing patient pk in v_compl_narrative
--
-- Revision 1.100  2004/09/18 00:19:24  ncq
-- - add v_compl_narrative
-- - add v_problem_list
-- - include is_significant in v_pat_episodes
--
-- Revision 1.99  2004/09/17 20:59:58  ncq
-- - remove cruft
-- - in v_pat_episodes UNION pull data from correct places ...
--
-- Revision 1.98  2004/09/17 20:28:05  ncq
-- - PG 7.4 is helpful: fix UNION
--
-- Revision 1.97  2004/09/17 20:14:06  ncq
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
-- Revision 1.96  2004/08/16 19:31:49  ncq
-- - add comments to views
-- - rewrite v_vacc_regimes to be distinct on fk_regime
-- - add v_vacc_defs4reg to list vaccination events for all
--   known schedules, this used to be v_vacc_regimes
-- - add v_vacc_regs4pat to list schedules a given patient
--   is on
-- - add v_vaccs_scheduled4pat to list vaccination events
--   that are scheduled for a patient according to the
--   schedules that patient is on
-- - rewrite v_pat_missing_vaccs/boosters based on the above
-- - matching grants
--
-- Revision 1.95  2004/08/11 08:59:54  ncq
-- - added v_pat_narrative by Carlos
--
-- Revision 1.94  2004/08/04 10:07:49  ncq
-- - added v_pat_item_types/v_types4item
--
-- Revision 1.93  2004/07/18 11:50:19  ncq
-- - added arbitrary typing of clin_root_items
--
-- Revision 1.92  2004/07/17 20:57:53  ncq
-- - don't use user/_user workaround anymore as we dropped supporting
--   it (but we did NOT drop supporting readonly connections on > 7.3)
--
-- Revision 1.91  2004/07/12 17:23:09  ncq
-- - allow for coding any SOAP row
-- - adjust views/tables to that
--
-- Revision 1.90  2004/07/07 15:07:34  ncq
-- - v_pat_diag_codes
-- - v_codes4diag
--
-- Revision 1.89  2004/07/05 22:47:34  ncq
-- - added pk_diag to v_coded_diag
--
-- Revision 1.88  2004/07/05 18:46:51  ncq
-- - fix grants
--
-- Revision 1.87  2004/07/05 17:47:13  ncq
-- - v_rfe/aoe -> v_pat_rfe/aoe
--
-- Revision 1.86  2004/07/04 16:31:09  ncq
-- - fix v_coded_diags: fk_diag=pk_diag
--
-- Revision 1.85  2004/07/04 16:14:41  ncq
-- - add grants
-- - I'm getting old
--
-- Revision 1.84  2004/07/04 16:12:44  ncq
-- - DROP INDEX cannot have ON clause, duh
--
-- Revision 1.83  2004/07/04 16:10:29  ncq
-- - add v_aoe/v_rfe
--
-- Revision 1.82  2004/07/03 17:24:08  ncq
-- - can't name all indexes the same :-)
--
-- Revision 1.81  2004/07/03 17:17:41  ncq
-- - indexes on clin_narrative
--
-- Revision 1.80  2004/07/02 15:00:10  ncq
-- - bring rfe/aoe/diag/coded_diag tables/views up to snuff and use them
--
-- Revision 1.79  2004/07/02 00:28:52  ncq
-- - clin_working_diag -> clin_coded_diag + index fixes therof
-- - v_pat_diag rewritten for clin_coded_diag, more useful now
-- - v_patient_items.id_item -> pk_item
-- - grants fixed
-- - clin_rfe/aoe folded into clin_narrative, that enhanced by
--   is_rfe/aoe with appropriate check constraint logic
-- - test data adapted to schema changes
--
-- Revision 1.78  2004/06/30 15:43:52  ncq
-- - clin_note -> clin_narrative
-- - remove v_i18n_curr_encounter
-- - add clin_rfe, clin_aoe
--
-- Revision 1.77  2004/06/28 15:04:31  ncq
-- - add pk_item to v_lab_requests
--
-- Revision 1.76  2004/06/28 12:38:30  ncq
-- - fixed on fk_ -> pk_
--
-- Revision 1.75  2004/06/28 12:15:38  ncq
-- - add view on lab_request -> v_lab_requests so we can fk_ -> pk_
--
-- Revision 1.74  2004/06/26 23:42:44  ncq
-- - indices on clin_root_item fields in descendants
-- - id_* -> fk/pk_*
--
-- Revision 1.73  2004/06/26 07:33:55  ncq
-- - id_episode -> fk/pk_episode
--
-- Revision 1.72  2004/06/13 08:08:35  ncq
-- - pull in some more PKs in views for episode/encounter/issue sorting
--
-- Revision 1.71  2004/06/02 00:05:51  ncq
-- - vpep.episode now vpep.description
--
-- Revision 1.70  2004/06/01 08:43:21  ncq
-- - fix grants re allergy_state
-- - include soap_cat in v_patient_items
--
-- Revision 1.69  2004/05/30 20:58:13  ncq
-- - encounter_type.id -> encounter_type.pk
--
-- Revision 1.68  2004/05/22 11:54:23  ncq
-- - cleanup signal handling on allergy table
--
-- Revision 1.67  2004/05/11 01:34:51  ncq
-- - allow test results with lab_request.is_pending is True in v_results4lab_req
--
-- Revision 1.66  2004/05/08 20:43:48  ncq
-- - eventually seem to have fixed latest_due/amount_overdue in v_pat_missing_boosters
--
-- Revision 1.65  2004/05/08 17:39:54  ncq
-- - remove v_i18n_enum_encounter_type
-- - _enum_encounter_type -> encounter_type
-- - add some _() uses
-- - improve v_pat_missing_vaccs/v_pat_missing_boosters
-- - cleanup/grants
--
-- Revision 1.64  2004/05/07 14:27:46  ncq
-- - first cut at amount_overdue for missing boosters (eg,
--   now() - (last_given + min_interval)) but doesn't work as
--   expecte for last_given is null despite coalesce(..., min_interval)
--
-- Revision 1.63  2004/05/06 23:34:52  ncq
-- - test_type_uni -> test_type_local
--
-- Revision 1.62  2004/05/02 19:25:21  ncq
-- - adapt to progress_note <-> description reversal in clin_working_diag
--
-- Revision 1.61  2004/04/30 12:22:31  ihaywood
-- new referral table
-- some changes to old medications tables, but still need more work
--
-- Revision 1.60  2004/04/30 09:20:09  ncq
-- - add v_pat_diag, grants
--
-- Revision 1.59  2004/04/30 09:12:30  ncq
-- - fk description clin_working_diag -> clin_aux_note
-- - v_pat_diag
--
-- Revision 1.58  2004/04/27 15:18:38  ncq
-- - rework diagnosis tables + grants for them
--
-- Revision 1.57  2004/04/26 21:17:10  ncq
-- - fix v_test_org_profile
--
-- Revision 1.56  2004/04/26 09:38:43  ncq
-- - enhance test_org_profile
--
-- Revision 1.55  2004/04/24 12:59:17  ncq
-- - all shiny and new, vastly improved vaccinations
--   handling via clinical item objects
-- - mainly thanks to Carlos Moro
--
-- Revision 1.54  2004/04/21 15:35:23  ihaywood
-- new referral table (do we still need gmclinical.form_data then?)
--
-- Revision 1.53  2004/04/21 15:30:24  ncq
-- - fix coalesce on unified_name/code in v_results4lab_req
-- - add unified_val
--
-- Revision 1.52  2004/04/20 00:17:56  ncq
-- - allergies API revamped, kudos to Carlos
--
-- Revision 1.51  2004/04/17 12:42:09  ncq
-- - add v_pat_encounters
--
-- Revision 1.50  2004/04/17 11:54:16  ncq
-- - v_patient_episodes -> v_pat_episodes
--
-- Revision 1.49  2004/04/07 18:16:06  ncq
-- - move grants into re-runnable scripts
-- - update *.conf accordingly
--
-- Revision 1.48  2004/03/23 17:34:49  ncq
-- - support and use optionally cross-provider unified test names
--
-- Revision 1.47  2004/03/23 02:33:13  ncq
-- - comments/constraints/references on test_result, also result_when -> clin_when
-- - v_results4lab_req, v_test_org_profile, grants
--
-- Revision 1.46  2004/03/19 10:55:40  ncq
-- - remove allergy.reaction -> use clin_root_item.narrative instead
--
-- Revision 1.45  2004/03/12 23:15:04  ncq
-- - adjust to id_ -> fk_/pk_
--
-- Revision 1.44  2004/02/18 15:29:05  ncq
-- - add v_most_recent_encounters
--
-- Revision 1.43  2004/02/02 16:17:42  ncq
-- - remove v_patient_vaccinations, v_pat_due_vaccs, v_pat_overdue_vaccs
-- - add v_pat_missing_vaccs, v_pat_missing_boosters
--
-- Revision 1.42  2004/01/26 20:08:16  ncq
-- - fk_recommended_by as pk_recommended_by
--
-- Revision 1.41  2004/01/26 18:26:04  ncq
-- - add/rename some FKs in views
--
-- Revision 1.40  2004/01/18 21:56:38  ncq
-- - v_patient_vacc4ind
-- - reformatting DDLs
--
-- Revision 1.39  2004/01/06 23:44:40  ncq
-- - __default__ -> xxxDEFAULTxxx
--
-- Revision 1.38  2003/12/29 15:31:53  uid66147
-- - rebuild v_vacc_regimes/v_patient_vaccinations/v_pat_due|overdue_vaccs due
--   to vaccination/vacc_def link normalization
-- - grants
--
-- Revision 1.37  2003/12/02 02:13:25  ncq
-- - we want UNIQUE indices on names.active etc
-- - add some i18n to views as well as some coalesce()
--
-- Revision 1.36  2003/11/28 10:07:52  ncq
-- - improve vaccination views
--
-- Revision 1.35  2003/11/28 01:03:48  ncq
-- - add views *_overdue_vaccs and *_due_vaccs
--
-- Revision 1.34  2003/11/26 23:54:51  ncq
-- - lnk_vaccdef2reg does not exist anymore
--
-- Revision 1.33  2003/11/18 17:52:37  ncq
-- - clin_date -> clin_when in v_patient_items
--
-- Revision 1.32  2003/11/16 19:34:29  ncq
-- - make partial index on __default__ encounters optional, fails on 7.1
--
-- Revision 1.31  2003/11/16 19:32:17  ncq
-- - clin_when in clin_root_item
--
-- Revision 1.30  2003/11/13 09:47:29  ncq
-- - use clin_date instead of date_given in vaccination
--
-- Revision 1.29  2003/11/09 22:45:45  ncq
-- - curr_encounter doesn't have id_patient anymore, fix trigger funcs
--
-- Revision 1.28  2003/11/09 14:54:56  ncq
-- - update view defs
--
-- Revision 1.27  2003/10/31 23:27:06  ncq
-- - clin_encounter now has fk_patient, hence v_i18n_patient_encounters
--   not needed anymore
-- - add v_i18n_curr_encounter view
-- - add v_patient_vaccinations view
--
-- Revision 1.26  2003/10/26 09:41:03  ncq
-- - truncate -> delete from
--
-- Revision 1.25  2003/10/19 15:43:00  ncq
-- - even better vaccination tables
--
-- Revision 1.24  2003/10/19 12:59:42  ncq
-- - add vaccination views (still flaky)
--
-- Revision 1.23  2003/08/03 14:06:45  ncq
-- - added measurements views
--
-- Revision 1.22  2003/07/19 20:23:47  ncq
-- - add clin_root_item triggers
-- - modify NOTIFY triggers so they include the patient ID
--   as per Ian's suggestion
--
-- Revision 1.21  2003/07/09 16:23:21  ncq
-- - add clin_health_issue triggers and functions
--
-- Revision 1.20  2003/06/29 15:24:22  ncq
-- - now clin_root_item inherits from audit_fields we can add
--    extract(epoch from modified_when) as age
--   to v_patient_items and order by that :-)
--
-- Revision 1.19  2003/06/22 16:23:35  ncq
-- - curr_encounter tracking triggers + grants
--
-- Revision 1.18  2003/06/03 13:49:06  ncq
-- - reorder v_patient_episodes/*_items for clarity
--
-- Revision 1.17  2003/06/01 11:38:12  ncq
-- - fix spelling of definate -> definite
--
-- Revision 1.16  2003/05/17 18:40:24  ncq
-- - notify triggers should come last, so make them zz*
--
-- Revision 1.15  2003/05/14 22:07:13  ncq
-- - adapt to changes in gmclinical.sql, particularly the narrative/item merge
--
-- Revision 1.14  2003/05/12 12:43:39  ncq
-- - gmI18N, gmServices and gmSchemaRevision are imported globally at the
--   database level now, don't include them in individual schema file anymore
--
-- Revision 1.13  2003/05/06 13:06:25  ncq
-- - pkey_ -> pk_
--
-- Revision 1.12  2003/05/05 11:59:50  ncq
-- - adapt to clin_narrative being an ancestor table
--
-- Revision 1.11  2003/05/05 00:31:28  ncq
-- - add grants
--
-- Revision 1.10  2003/05/05 00:27:34  ncq
-- - add as to encounter types
--
-- Revision 1.9  2003/05/05 00:19:12  ncq
-- - we do need the v_i18n_ on encounter types
--
-- Revision 1.8  2003/05/04 23:35:59  ncq
-- - major reworking to follow the formal EMR structure writeup
--
-- Revision 1.7  2003/05/03 00:44:05  ncq
-- - make patient allergies view work
--
-- Revision 1.6  2003/05/02 15:06:19  ncq
-- - make trigger return happy
-- - tweak v_i18n_patient_allergies - not done yet
--
-- Revision 1.5  2003/05/01 15:05:36  ncq
-- - function/trigger to announce insertion/deletion of allergy
-- - allergy.id_substance -> allergy.substance_code
--
-- Revision 1.4  2003/04/30 23:30:29  ncq
-- - v_i18n_patient_allergies
-- - new_allergy -> allergy_new
--
-- Revision 1.3  2003/04/29 12:34:54  ncq
-- - added more views + grants
--
-- Revision 1.2  2003/04/28 21:39:49  ncq
-- - cleanups and GRANTs
--
-- Revision 1.1  2003/04/28 20:40:48  ncq
-- - this can safely be dropped and recreated even with data in the tables
--
