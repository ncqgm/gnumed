-- project: GnuMed

-- purpose: views for easier clinical data access
-- author: Karsten Hilbert
-- license: GPL (details at http://gnu.org)

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmClinicalViews.sql,v $
-- $Id: gmClinicalViews.sql,v 1.138 2005-04-03 20:14:04 ncq Exp $

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
\unset ON_ERROR_STOP
drop index idx_cri_encounter;
drop index idx_cri_episode;

drop index idx_clnarr_encounter;
drop index idx_clnarr_episode;

drop index idx_clanote_encounter;
drop index idx_clanote_episode;

drop index idx_vacc_encounter;
drop index idx_vacc_episode;

drop index idx_allg_encounter;
drop index idx_allg_episode;

drop index idx_formi_encounter;
drop index idx_formi_episode;

drop index idx_cmeds_encounter;
drop index idx_cmeds_episode;

drop index idx_ref_encounter;
drop index idx_ref_episode;

drop index idx_tres_encounter;
drop index idx_tres_episode;

drop index idx_lreq_encounter;
drop index idx_lreq_episode;

\set ON_ERROR_STOP 1

-- clin_root_item & children indices
create index idx_cri_encounter on clin_root_item(fk_encounter);
create index idx_cri_episode on clin_root_item(fk_episode);

create index idx_clnarr_encounter on clin_narrative(fk_encounter);
create index idx_clnarr_episode on clin_narrative(fk_episode);

create index idx_clanote_encounter on clin_aux_note(fk_encounter);
create index idx_clanote_episode on clin_aux_note(fk_episode);

create index idx_vacc_encounter on vaccination(fk_encounter);
create index idx_vacc_episode on vaccination(fk_episode);

create index idx_allg_encounter on allergy(fk_encounter);
create index idx_allg_episode on allergy(fk_episode);

create index idx_formi_encounter on form_instances(fk_encounter);
create index idx_formi_episode on form_instances(fk_episode);

create index idx_cmeds_encounter on clin_medication(fk_encounter);
create index idx_cmeds_episode on clin_medication(fk_episode);

create index idx_ref_encounter on referral(fk_encounter);
create index idx_ref_episode on referral(fk_episode);

create index idx_tres_encounter on test_result(fk_encounter);
create index idx_tres_episode on test_result(fk_episode);

create index idx_lreq_encounter on lab_request(fk_encounter);
create index idx_lreq_episode on lab_request(fk_episode);

-- =============================================
-- narrative
\unset ON_ERROR_STOP

drop index idx_narr_soap;
drop index idx_narr_s;
drop index idx_narr_o;
drop index idx_narr_a;
drop index idx_narr_p;
drop index idx_narr_rfe;
drop index idx_narr_aoe;

create index idx_narr_s on clin_narrative(soap_cat) where soap_cat='s';
create index idx_narr_o on clin_narrative(soap_cat) where soap_cat='o';
create index idx_narr_a on clin_narrative(soap_cat) where soap_cat='a';
create index idx_narr_p on clin_narrative(soap_cat) where soap_cat='p';
create index idx_narr_rfe on clin_narrative(is_rfe) where is_rfe is true;
create index idx_narr_aoe on clin_narrative(is_aoe) where is_aoe is true;

\set ON_ERROR_STOP 1

create index idx_narr_soap on clin_narrative(soap_cat);

-- clin_medication
\unset ON_ERROR_STOP
drop index idx_clin_medication;
create index idx_clin_medication on clin_medication(discontinued) where discontinued is not null;
\set ON_ERROR_STOP 1


-- =============================================
-- encounters

\unset ON_ERROR_STOP
drop trigger tr_set_encounter_timezone on clin_encounter;
drop function f_set_encounter_timezone();
\set ON_ERROR_STOP 1

create function f_set_encounter_timezone() returns opaque as '
begin
	if TG_OP = ''INSERT'' then
		NEW.source_time_zone := (select (extract(timezone from (select now()))::text || ''seconds'')::interval);
	else
		NEW.source_time_zone := OLD.source_time_zone;
	end if;
	return NEW;
end;
' language 'plpgsql';

create trigger tr_set_encounter_timezone
	before insert or update
	on clin_encounter
	for each row
		execute procedure f_set_encounter_timezone()
;

-- per patient
\unset ON_ERROR_STOP
drop view v_pat_encounters;
\set ON_ERROR_STOP 1

create view v_pat_encounters as
select
	cle.id as pk_encounter,
	cle.fk_patient as pk_patient,
	cle.started as started,
	et.description as type,
	_(et.description) as l10n_type,
	cle.description as description,
	cle.last_affirmed as last_affirmed,
	cle.fk_location as pk_location,
	cle.fk_provider as pk_provider,
	cle.fk_type as pk_type,
	cle.xmin as xmin_clin_encounter
from
	clin_encounter cle,
	encounter_type et
where
	cle.fk_type = et.pk
;

-- current ones
\unset ON_ERROR_STOP
drop view v_most_recent_encounters;
\set ON_ERROR_STOP 1

create view v_most_recent_encounters as
select distinct on (last_affirmed)
	ce1.id as pk_encounter,
	ce1.fk_patient as pk_patient,
	ce1.description as description,
	et.description as type,
	_(et.description) as l10n_type,
	ce1.started as started,
	ce1.last_affirmed as last_affirmed,
	ce1.fk_type as pk_type,
	ce1.fk_location as pk_location,
	ce1.fk_provider as pk_provider
from
	clin_encounter ce1,
	encounter_type et
where
	ce1.fk_type = et.pk
		and
	ce1.id = (
		select max(id)
		from clin_encounter ce2
		where
			ce2.fk_patient = ce1.fk_patient
				and
			ce2.started = (
				select max(started)
				from clin_encounter ce3
				where
					ce3.fk_patient = ce2.fk_patient
						and
					ce3.last_affirmed = (
						select max(last_affirmed)
						from clin_encounter ce4
						where ce4.fk_patient = ce3.fk_patient
					)
			)
	)
;
-- =============================================
-- episodes stuff

-- speed up access by fk_health_issue
\unset ON_ERROR_STOP
drop index idx_episode_issue;
drop index idx_episode_valid_issue;
create index idx_episode_valid_issue on clin_episode(fk_health_issue) where fk_health_issue is not null;
\set ON_ERROR_STOP 1
create index idx_episode_issue on clin_episode(fk_health_issue);


\unset ON_ERROR_STOP
drop trigger tr_episode_mod on clin_episode;
drop function trf_announce_episode_mod();
\set ON_ERROR_STOP 1

create function trf_announce_episode_mod() returns opaque as '
declare
	patient_id integer;
begin
	-- get patient ID
	if TG_OP = ''DELETE'' then
		-- if no patient in episode
		if OLD.fk_patient is null then
			-- get it from attached health issue
			select into patient_id id_patient
				from clin_health_issue
				where id = OLD.fk_health_issue;
		else
			patient_id := OLD.fk_patient;
		end if;
	else
		-- if no patient in episode
		if NEW.fk_patient is null then
			-- get it from attached health issue
			select into patient_id id_patient
				from clin_health_issue
				where id = NEW.fk_health_issue;
		else
			patient_id := NEW.fk_patient;
		end if;
	end if;
	-- execute() the NOTIFY
	execute ''notify "episode_change_db:'' || patient_id || ''"'';
	return NULL;
end;
' language 'plpgsql';

create trigger tr_episode_mod
	after insert or delete or update
	on clin_episode
	for each row
		execute procedure trf_announce_episode_mod()
;

\unset ON_ERROR_STOP
drop view v_pat_episodes cascade;
drop view v_pat_episodes;
\set ON_ERROR_STOP 1

create view v_pat_episodes as
select
	cep.fk_patient as pk_patient,
	cep.description as description,
	cep.is_open as episode_open,
	null as health_issue,
	null as issue_active,
	null as issue_clinically_relevant,
	cep.pk as pk_episode,
	null as pk_health_issue,
	cep.modified_when as episode_modified_when,
	cep.modified_by as episode_modified_by,
	cep.xmin as xmin_clin_episode
from
	clin_episode cep
where
	cep.fk_health_issue is null

		UNION ALL

select
	chi.id_patient as pk_patient,
	cep.description as description,
	cep.is_open as episode_open,
	chi.description as health_issue,
	chi.is_active as issue_active,
	chi.clinically_relevant as issue_clinically_relevant,
	cep.pk as pk_episode,
	cep.fk_health_issue as pk_health_issue,
	cep.modified_when as episode_modified_when,
	cep.modified_by as episode_modified_by,
	cep.xmin as xmin_clin_episode
from
	clin_episode cep, clin_health_issue chi
where
	-- this should exclude all (fk_health_issue is Null) ?
	cep.fk_health_issue=chi.id
;

-- =============================================
-- clin_root_item stuff
\unset ON_ERROR_STOP
drop trigger TR_clin_item_mod on clin_root_item;
drop function f_announce_clin_item_mod();
\set ON_ERROR_STOP 1

create function F_announce_clin_item_mod() returns opaque as '
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
		from v_pat_episodes vpep
		where vpep.pk_episode = episode_id
		limit 1;
	-- now, execute() the NOTIFY
	execute ''notify "item_change_db:'' || patient_id || ''"'';
	return NULL;
end;
' language 'plpgsql';

create trigger TR_clin_item_mod
	after insert or delete or update
	on clin_root_item
	for each row
		execute procedure f_announce_clin_item_mod()
;

-- ---------------------------------------------
-- protect from direct inserts/updates/deletes which the
-- inheritance system can't handle properly
\unset ON_ERROR_STOP
drop function f_protect_clin_root_item();
drop rule clin_ritem_no_ins on clin_root_item cascade;
drop rule clin_ritem_no_ins;
drop rule clin_ritem_no_upd on clin_root_item cascade;
drop rule clin_ritem_no_upd;
drop rule clin_ritem_no_del on clin_root_item cascade;
drop rule clin_ritem_no_del;
\set ON_ERROR_STOP 1

create function f_protect_clin_root_item() returns opaque as '
begin
	raise exception ''INSERT/UPDATE/DELETE on <clin_root_item> not allowed.'';
	return NULL;
end;
' language 'plpgsql';

create rule clin_ritem_no_ins as
	on insert to clin_root_item
	do instead select f_protect_clin_root_item();

create rule clin_ritem_no_upd as
	on update to clin_root_item
	do instead select f_protect_clin_root_item();

create rule clin_ritem_no_del as
	on delete to clin_root_item
	do instead select f_protect_clin_root_item();

-- ---------------------------------------------
\unset ON_ERROR_STOP
drop view v_pat_items;
\set ON_ERROR_STOP 1

create view v_pat_items as
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
	clin_root_item cri,
	v_pat_episodes vpep,
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
drop view v_test_type_unified cascade;
drop view v_test_type_unified;
\set ON_ERROR_STOP 1

create view v_test_type_unified as
select
	ttu.pk as pk_test_type_unified,
	ltt2ut.fk_test_type as pk_test_type,
	ttu.code as code_unified,
	ttu.name as name_unified,
	ttu.coding_system as coding_system_unified,
	ttu.comment as comment_unified,
	ltt2ut.pk as pk_lnk_ttype2unified_type
from
	test_type_unified ttu,
	lnk_ttype2unified_type ltt2ut
where
	ltt2ut.fk_test_type_unified=ttu.pk
;

comment on view v_test_type_unified is
	'denormalized view of test_type_unified and link table to test_type';

--
\unset ON_ERROR_STOP
drop view v_unified_test_types cascade;
drop view v_unified_test_types;
\set ON_ERROR_STOP 1

create view v_unified_test_types as
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
	(test_type tt1 left outer join v_test_type_unified vttu1 on (tt1.pk=vttu1.pk_test_type)) ttu0
;

comment on view v_unified_test_types is
	'provides a view of test types aggregated under their
	 corresponding unified name if any, if not linked to a
	 unified test type name the original name is used';


--
\unset ON_ERROR_STOP
drop view v_test_org_profile cascade;
drop view v_test_org_profile;
\set ON_ERROR_STOP 1

create view v_test_org_profile as
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
	test_org torg,
	v_unified_test_types vttu
where
	vttu.pk_test_org=torg.pk
;

comment on view v_test_org_profile is
	'the tests a given test org provides';


--
\unset ON_ERROR_STOP
drop view v_test_results cascade;
drop view v_test_results;
\set ON_ERROR_STOP 1

create view v_test_results as
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
	tr.reviewed_by_clinician,
	tr.clinically_relevant,
	tr.technically_abnormal,
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
	-- clin_root_item
	tr.pk_item,
	tr.fk_encounter as pk_encounter,
	tr.fk_episode as pk_episode,
	-- test_result
	tr.fk_type as pk_test_type,
	tr.fk_reviewer as pk_reviewer,
	tr.modified_when,
	tr.modified_by,
	tr.xmin as xmin_test_result,
	-- v_unified_test_types
	vttu.pk_test_org,
	vttu.pk_test_type_unified,
	-- v_pat_episodes
	vpe.pk_health_issue
from
	test_result tr,
	v_unified_test_types vttu,
	v_pat_episodes vpe
where
	vttu.pk_test_type=tr.fk_type
		and
	tr.fk_episode=vpe.pk_episode
;

comment on view v_test_results is
	'denormalized view over test_results joined with (possibly unified) test
	 type and patient/episode/encounter keys';


--
\unset ON_ERROR_STOP
drop view v_lab_requests;
\set ON_ERROR_STOP 1

create view v_lab_requests as
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
	lab_request lr,
	test_org torg,
	v_pat_items vpi
where
	lr.fk_test_org=torg.pk
		and
	vpi.pk_item = lr.pk_item
;

comment on view v_lab_requests is
	'denormalizes lab requests per test organization';


--
\unset ON_ERROR_STOP
drop view v_results4lab_req;
\set ON_ERROR_STOP 1

create view v_results4lab_req as
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
	vtr.technically_abnormal as abnormal,
	vtr.clinically_relevant as relevant,
	vtr.note_provider,
	lr.request_status as request_status,
	vtr.norm_ref_group as ref_group,
	lr.request_id,
	lr.lab_request_id,
	vtr.material,
	vtr.material_detail,
	vtr.reviewed_by_clinician as reviewed,
	vtr.pk_reviewer,
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
	v_test_results vtr,
	lab_request lr,
	lnk_result2lab_req lr2lr
where
	lr2lr.fk_result=vtr.pk_test_result
		and
	lr2lr.fk_request=lr.pk
;

comment on view v_results4lab_req is
	'shows denormalized lab results per request';


-- ==========================================================
-- health issues stuff
\unset ON_ERROR_STOP
drop trigger TR_h_issues_modified on clin_health_issue;
drop function F_announce_h_issue_mod();
\set ON_ERROR_STOP 1

create function F_announce_h_issue_mod() returns opaque as '
declare
	patient_id integer;
begin
	-- get patient ID
	if TG_OP = ''DELETE'' then
		patient_id := OLD.id_patient;
	else
		patient_id := NEW.id_patient;
	end if;
	-- now, execute() the NOTIFY
	execute ''notify "health_issue_change_db:'' || patient_id || ''"'';
	return NULL;
end;
' language 'plpgsql';

create trigger TR_h_issues_modified
	after insert or delete or update
	on clin_health_issue
	for each row
		execute procedure F_announce_h_issue_mod()
;

-- ==========================================================
-- allergy stuff
\unset ON_ERROR_STOP
drop view v_pat_allergies;
\set ON_ERROR_STOP 1

create view v_pat_allergies as
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
	allergy a,
	_enum_allergy_type at,
	v_pat_episodes vpep
where
	vpep.pk_episode=a.fk_episode
		and
	at.id=a.id_type
;

-- ==========================================================
-- vaccination stuff
-- -----------------------------------------------------
\unset ON_ERROR_STOP
drop view v_vacc_regimes cascade;
drop view v_vacc_regimes;
\set ON_ERROR_STOP 1

create view v_vacc_regimes as
select
	vreg.id as pk_regime,
	vind.description as indication,
	_(vind.description) as l10n_indication,
	vreg.name as regime,
	(select max(vdef.seq_no) from vacc_def vdef where vreg.id = vdef.fk_regime) as shots,
	coalesce(vreg.comment, '') as comment,
	vreg.fk_indication as pk_indication,
	vreg.fk_recommended_by as pk_recommended_by,
	vreg.xmin as xmin_vacc_regime
from
	vacc_regime vreg,
	vacc_indication vind
where
	vreg.fk_indication = vind.id
;

comment on view v_vacc_regimes is
	'all vaccination schedules known to the system';

-- -----------------------------------------------------
\unset ON_ERROR_STOP
drop view v_vacc_defs4reg;
\set ON_ERROR_STOP 1

create view v_vacc_defs4reg as
select
	vreg.id as pk_regime,
	vind.description as indication,
	_(vind.description) as l10n_indication,
	vreg.name as regime,
	coalesce(vreg.comment, '') as reg_comment,
	vdef.id as pk_vacc_def,
	vdef.is_booster as is_booster,
	vdef.seq_no as vacc_seq_no,
	vdef.min_age_due as age_due_min,
	vdef.max_age_due as age_due_max,
	vdef.min_interval as min_interval,
	coalesce(vdef.comment, '') as vacc_comment,
	vind.id as pk_indication,
	vreg.fk_recommended_by as pk_recommended_by
from
	vacc_regime vreg,
	vacc_indication vind,
	vacc_def vdef
where
	vreg.id = vdef.fk_regime
		and
	vreg.fk_indication = vind.id
order by
	indication,
	vacc_seq_no
;

comment on view v_vacc_defs4reg is
	'vaccination event definitions for all schedules known to the system';

-- -----------------------------------------------------
\unset ON_ERROR_STOP
drop view v_vacc_regs4pat;
\set ON_ERROR_STOP 1

create view v_vacc_regs4pat as
select
	lp2vr.fk_patient as pk_patient,
	vvr.indication as indication,
	vvr.l10n_indication as l10n_indication,
	vvr.regime as regime,
	vvr.comment as comment,
	vvr.pk_regime as pk_regime,
	vvr.pk_indication as pk_indication,
	vvr.pk_recommended_by as pk_recommended_by
from
	lnk_pat2vacc_reg lp2vr,
	v_vacc_regimes vvr
where
	vvr.pk_regime = lp2vr.fk_regime
;

comment on view v_vacc_regs4pat is
	'selection of configured vaccination schedules a patient is actually on';

-- -----------------------------------------------------
\unset ON_ERROR_STOP
drop view v_vaccs_scheduled4pat;
\set ON_ERROR_STOP 1

create view v_vaccs_scheduled4pat as
select
	vvr4p.pk_patient as pk_patient,
	vvr4p.indication as indication,
	vvr4p.l10n_indication as l10n_indication,
	vvr4p.regime as regime,
	vvr4p.comment as reg_comment,
	vvd4r.is_booster,
	vvd4r.vacc_seq_no,
	vvd4r.age_due_min,
	vvd4r.age_due_max,
	vvd4r.min_interval,
	vvd4r.vacc_comment as vacc_comment,
	vvd4r.pk_vacc_def as pk_vacc_def,
	vvr4p.pk_regime as pk_regime,
	vvr4p.pk_indication as pk_indication,
	vvr4p.pk_recommended_by as pk_recommended_by
from
	v_vacc_regs4pat vvr4p,
	v_vacc_defs4reg vvd4r
where
	vvd4r.pk_regime = vvr4p.pk_regime
;

comment on view v_vaccs_scheduled4pat is
	'vaccinations scheduled for a patient according
	 to the vaccination schedules he/she is on';

-- -----------------------------------------------------
\unset ON_ERROR_STOP
drop view v_pat_vacc4ind;
\set ON_ERROR_STOP 1

create view v_pat_vacc4ind as
select
	v.fk_patient as pk_patient,
	v.id as pk_vaccination,
	v.clin_when as date,
	vind.description as indication,
	_(vind.description) as l10n_indication,
	vcine.trade_name as vaccine,
	vcine.short_name as vaccine_short,
	v.batch_no as batch_no,
	v.site as site,
	coalesce(v.narrative, '') as narrative,
	vind.id as pk_indication,
	v.fk_provider as pk_provider,
	vcine.id as pk_vaccine,
	vpep.pk_health_issue as pk_health_issue,
	v.fk_episode as pk_episode,
	v.fk_encounter as pk_encounter,
	v.modified_when as modified_when,
	v.modified_by as modified_by,
	v.xmin as xmin_vaccination
from
	vaccination v,
	vaccine vcine,
	lnk_vaccine2inds lv2i,
	vacc_indication vind,
	v_pat_episodes vpep
where
	vpep.pk_episode=v.fk_episode
		and
	v.fk_vaccine = vcine.id
		and
	lv2i.fk_vaccine = vcine.id
		and
	lv2i.fk_indication = vind.id
;

comment on view v_pat_vacc4ind is
	'vaccinations a patient has actually received for the various
	 indications, we operate under the assumption that every shot
	 given counts toward base immunisation, eg. all shots are valid';

-- -----------------------------------------------------
\unset ON_ERROR_STOP
drop view v_pat_missing_vaccs;
\set ON_ERROR_STOP 1

create view v_pat_missing_vaccs as
select
	vvs4p.pk_patient,
	vvs4p.indication,
	vvs4p.l10n_indication,
	vvs4p.regime,
	vvs4p.reg_comment,
	vvs4p.vacc_seq_no as seq_no,
	case when vvs4p.age_due_max is null
		then (now() + coalesce(vvs4p.min_interval, vvs4p.age_due_min))
		else ((select identity.dob from identity where identity.pk=vvs4p.pk_patient) + vvs4p.age_due_max)
	end as latest_due,
	-- note that ...
	-- ... 1) time_left ...
	case when vvs4p.age_due_max is null
		then coalesce(vvs4p.min_interval, vvs4p.age_due_min)
		else (((select identity.dob from identity where identity.pk=vvs4p.pk_patient) + vvs4p.age_due_max) - now())
	end as time_left,
	-- ... and 2) amount_overdue ...
	case when vvs4p.age_due_max is null
		then coalesce(vvs4p.min_interval, vvs4p.age_due_min)
		else (now() - ((select identity.dob from identity where identity.pk=vvs4p.pk_patient) + vvs4p.age_due_max))
	end as amount_overdue,
	-- ... are just the inverse of each other
	vvs4p.age_due_min,
	vvs4p.age_due_max,
	vvs4p.min_interval,
	vvs4p.vacc_comment,
	vvs4p.pk_regime,
	vvs4p.pk_indication,
	vvs4p.pk_recommended_by
from
	v_vaccs_scheduled4pat vvs4p
where
	vvs4p.is_booster is false
		and
	vvs4p.vacc_seq_no > (
		select count(*)
		from v_pat_vacc4ind vpv4i
		where
			vpv4i.pk_patient = vvs4p.pk_patient
				and
			vpv4i.indication = vvs4p.indication
	)
;

comment on view v_pat_missing_vaccs is
	'vaccinations a patient has not been given yet according
	 to the schedules a patient is on and the previously
	 received vaccinations';

-- -----------------------------------------------------
\unset ON_ERROR_STOP
drop view v_pat_missing_boosters;
\set ON_ERROR_STOP 1

-- FIXME: only list those that DO HAVE a previous vacc (max(date) is not null)
create view v_pat_missing_boosters as
select
	vvs4p.pk_patient,
	vvs4p.indication,
	vvs4p.l10n_indication,
	vvs4p.regime,
	vvs4p.reg_comment,
	vvs4p.vacc_seq_no as seq_no,
	coalesce(
		((select max(vpv4i11.date)
		  from v_pat_vacc4ind vpv4i11
		  where
			vpv4i11.pk_patient = vvs4p.pk_patient
				and
			vpv4i11.indication = vvs4p.indication
		) + vvs4p.min_interval),
		(now() - '1 day'::interval)
	) as latest_due,
	coalesce(
		(now() - (
			(select max(vpv4i12.date)
			from v_pat_vacc4ind vpv4i12
			where
				vpv4i12.pk_patient = vvs4p.pk_patient
					and
				vpv4i12.indication = vvs4p.indication) + vvs4p.min_interval)
		),
		'1 day'::interval
	) as amount_overdue,
	vvs4p.age_due_min,
	vvs4p.age_due_max,
	vvs4p.min_interval,
	vvs4p.vacc_comment,
	vvs4p.pk_regime,
	vvs4p.pk_indication,
	vvs4p.pk_recommended_by
from
	v_vaccs_scheduled4pat vvs4p
where
	vvs4p.is_booster is true
		and
	vvs4p.min_interval < age (
		(select max(vpv4i13.date)
			from v_pat_vacc4ind vpv4i13
			where
				vpv4i13.pk_patient = vvs4p.pk_patient
					and
				vpv4i13.indication = vvs4p.indication
		))
;

comment on view v_pat_missing_boosters is
	'boosters a patient has not been given yet according
	 to the schedules a patient is on and the previously
	 received vaccinations';

-- ==========================================================
-- current encounter stuff
\unset ON_ERROR_STOP
drop trigger at_curr_encounter_ins on curr_encounter;
drop function f_curr_encounter_force_ins();

drop trigger at_curr_encounter_upd on curr_encounter;
drop function f_curr_encounter_force_upd();
\set ON_ERROR_STOP 1

create function f_curr_encounter_force_ins() returns opaque as '
begin
	NEW.started := CURRENT_TIMESTAMP;
	NEW.last_affirmed := CURRENT_TIMESTAMP;
	return NEW;
end;
' language 'plpgsql';

create trigger at_curr_encounter_ins
	before insert on curr_encounter
	for each row execute procedure f_curr_encounter_force_ins()
;
-- should really be "for each statement" but that isn't supported yet by PostgreSQL

create function f_curr_encounter_force_upd() returns opaque as '
begin
	NEW.fk_encounter := OLD.fk_encounter;
	NEW.started := OLD.started;
	NEW.last_affirmed := CURRENT_TIMESTAMP;
	return NEW;
end;
' language 'plpgsql';

create trigger at_curr_encounter_upd
	before update on curr_encounter
	for each row execute procedure f_curr_encounter_force_upd()
;
-- should really be "for each statement" but that isn't supported yet by PostgreSQL

-- =============================================
-- diagnosis views
\unset ON_ERROR_STOP
drop view v_pat_diag;
\set ON_ERROR_STOP 1

create view v_pat_diag as
select
	vpi.pk_patient as pk_patient,
	cd.pk as pk_diag,
	cd.fk_narrative as pk_narrative,
	cn.clin_when as diagnosed_when,
	cn.narrative as diagnosis,
	cd.laterality as laterality,
	cd.is_chronic as is_chronic,
	cd.is_active as is_active,
	cd.is_definite as is_definite,
	cd.clinically_relevant as clinically_relevant,
	cn.fk_encounter as pk_encounter,
	cn.fk_episode as pk_episode,
	cd.xmin as xmin_clin_diag,
	cn.xmin as xmin_clin_narrative
from
	clin_diag cd,
	clin_narrative as cn,
	v_pat_items vpi
where
	cn.soap_cat='a'
		and
	cd.fk_narrative = cn.pk
		and
	cn.pk_item = vpi.pk_item
;

-- this view has a row for each code-per-diagnosis-per-patient,
-- hence one patient-diagnosis can appear several times, namely
-- once per associated code
\unset ON_ERROR_STOP
drop view v_pat_diag_codes;
\set ON_ERROR_STOP 1

-- FIXME: patient missing
create view v_pat_diag_codes as
select
	vpd.pk_diag as pk_diag,
	vpd.diagnosis as diagnosis,
	lc2n.code as code,
	lc2n.xfk_coding_system as coding_system
from
	v_pat_diag vpd,
	lnk_code2narr lc2n
where
	lc2n.fk_narrative = vpd.pk_narrative
;

-- this view is a lookup table for locally used
-- code/diagnosis associations irrespective of
-- patient association, hence any diagnosis-code
-- combination will appear only once
\unset ON_ERROR_STOP
drop view v_codes4diag;
\set ON_ERROR_STOP 1

create view v_codes4diag as
select distinct on (diagnosis, code, xfk_coding_system)
	vpd.diagnosis as diagnosis,
	lc2n.code as code,
	lc2n.xfk_coding_system as coding_system
from
	v_pat_diag vpd,
	lnk_code2narr lc2n
where
	lc2n.fk_narrative = vpd.pk_narrative
;


-- =============================================
-- types of narrative

\unset ON_ERROR_STOP
drop view v_pat_rfe;
\set ON_ERROR_STOP 1

create view v_pat_rfe as
select
	vpi.pk_patient as pk_patient,
	cn.pk as pk_narrative,
	cn.clin_when as clin_when,
	cn.soap_cat as soap_cat,
	cn.narrative as rfe,
	cn.fk_encounter as pk_encounter,
	cn.fk_episode as pk_episode,
	cn.pk_item as pk_item,
	cn.xmin as xmin_clin_narrative
from
	clin_narrative cn,
	v_pat_items vpi
where
	cn.is_rfe is true
		and
	cn.pk_item = vpi.pk_item
;


\unset ON_ERROR_STOP
drop view v_pat_aoe;
\set ON_ERROR_STOP 1

create view v_pat_aoe as
select
	vpi.pk_patient as pk_patient,
	cn.pk as pk_narrative,
	cn.clin_when as clin_when,
	cn.soap_cat as soap_cat,
	cn.narrative as aoe,
	cn.fk_encounter as pk_encounter,
	cn.fk_episode as pk_episode,
	cn.pk_item as pk_item,
	cn.xmin as xmin_clin_narrative
from
	clin_narrative cn,
	v_pat_items vpi
where
	cn.is_aoe is true
		and
	cn.pk_item = vpi.pk_item
;

\unset ON_ERROR_STOP
drop view v_pat_narrative;
\set ON_ERROR_STOP 1

-- might be slow
create view v_pat_narrative as
select
	vpi.pk_patient as pk_patient,
	cn.clin_when as date,
	cn.soap_cat as soap_cat,
	cn.narrative as narrative,
	cn.is_aoe as is_aoe,
	cn.is_rfe as is_rfe,
	cn.pk_item as pk_item,
	cn.pk as pk_narrative,
	vpi.pk_health_issue as pk_health_issue,
	cn.fk_episode as pk_episode,
	cn.fk_encounter as pk_encounter,
	vpe.pk_provider as pk_provider,
	cn.xmin as xmin_clin_narrative
from
	clin_narrative cn,
	v_pat_items vpi,
	v_pat_encounters vpe
where
	cn.pk_item = vpi.pk_item
		and
	vpi.pk_encounter = vpe.pk_encounter
;

comment on view v_pat_narrative is
	'patient SOAP narrative';

-- =============================================
-- types of clin_root_item

-- ---------------------------------------------
-- custom referential integrity
\unset ON_ERROR_STOP
drop trigger tr_rfi_type2item on lnk_type2item cascade;
drop trigger tr_rfi_type2item on lnk_type2item;
drop function f_rfi_type2item();
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
	select into dummy 1 from clin_root_item where pk_item=NEW.fk_item;
	if not found then
		msg := ''referential integrity violation: lnk_type2item.fk_item ['' || NEW.fk_item || ''] not in <clin_root_item.pk_item>'';
		raise exception ''%'', msg;
		return NULL;
	end if;
	return NEW;
end;
' language 'plpgsql';

create trigger tr_rfi_type2item
	after insert or update
	on lnk_type2item
	for each row
		execute procedure f_rfi_type2item()
;

comment on function f_rfi_type2item() is
	'function used to check referential integrity from
	 lnk_type2item to clin_root_item with a custom trigger';

--comment on trigger tr_rfi_type2item is
--	'trigger to check referential integrity from
--	 lnk_type2item to clin_root_item';

-- ---------------------------------------------
\unset ON_ERROR_STOP
drop view v_pat_item_types;
\set ON_ERROR_STOP 1

create view v_pat_item_types as
select
	items.pk_item as pk_item,
	items.pk_patient as pk_patient,
	items.code as code,
	items.narrative as narrative,
	items.type as type
from
	((v_pat_items vpi inner join lnk_type2item lt2i on (vpi.pk_item=lt2i.fk_item)) lnkd_items
		inner join clin_item_type cit on (lnkd_items.fk_type=cit.pk)) items
;

-- ---------------------------------------------
\unset ON_ERROR_STOP
drop view v_types4item;
\set ON_ERROR_STOP 1

create view v_types4item as
select distinct on (narrative, code, type, src_table)
	items.code as code,
	items.narrative as narrative,
	items.type as type,
	items.soap_cat as soap_cat,
	items.src_table as src_table
from
	((v_pat_items vpi inner join lnk_type2item lt2i on (vpi.pk_item=lt2i.fk_item)) lnkd_items
		inner join clin_item_type cit on (lnkd_items.fk_type=cit.pk)) items
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
--		fk_item = (select pk_item from clin_narrative where pk=NEW.fk_narrative)
--			and
--		fk_type = (select pk from clin_item_type )
--	;
--	if not found then
--		msg := ''referential integrity violation: lnk_type2item.fk_item ['' || NEW.fk_item || ''] not in <clin_root_item.pk_item>'';
--		raise exception ''%'', msg;
--		return NULL;
--	end if;
--	return NEW;
--end;
--' language 'plpgsql';

--create trigger tr_rfi_type2item
--	after insert or update
--	on lnk_type2item
--	for each row
--		execute procedure f_rfi_type2item()
--;

--comment on function f_rfi_type2item() is
--	'function used to check referential integrity from
--	 lnk_type2item to clin_root_item with a custom trigger';

--comment on trigger tr_rfi_type2item is
--	'trigger to check referential integrity from
--	 lnk_type2item to clin_root_item';

\unset ON_ERROR_STOP
drop view v_hx_family;
\set ON_ERROR_STOP 1

create view v_hx_family as
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
	v_pat_items vpi,
	clin_hx_family chxf,
	hx_family_item hxfi,
	v_basic_person vbp
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
	v_pat_items vpi,
	clin_hx_family chxf,
	hx_family_item hxfi,
	v_basic_person vbp
where
	vpi.pk_item = chxf.pk_item
		and
	hxfi.pk = chxf.fk_hx_family_item
		and
	hxfi.fk_narrative_condition is null
		and
	hxfi.fk_relative = v_basic_person.pk_identity

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
	clin_hx_family chxf,
	hx_family_item hxfi,
	v_basic_person vbp,
	v_pat_narrative vpn
where
	hxfi.pk = chxf.fk_hx_family_item
		and
	hxfi.fk_narrative_condition = vpn.pk_narrative
		and
	hxfi.fk_relative is null
		and
	v_basic_person.pk_identity = vpn.pk_patient
;


-- =============================================
-- problem list

\unset ON_ERROR_STOP
drop view v_problem_list;
\set ON_ERROR_STOP 1

create view v_problem_list as
select	-- all the episodes
	vpep.pk_patient as pk_patient,
	vpep.description as problem,
	'episode' as type,
	vpep.episode_open as problem_active,
	'true'::boolean as clinically_relevant,
	vpep.pk_episode as pk_episode,
	vpep.pk_health_issue as pk_health_issue
from
	v_pat_episodes vpep

union	-- and

select	-- all the issues
	chi.id_patient as pk_patient,
	chi.description as problem,
	'issue' as type,
	chi.is_active as problem_active,
	chi.clinically_relevant as clinically_relevant,
	null as pk_episode,
	chi.id as pk_health_issue
from
	clin_health_issue chi
;

-- =============================================
-- *complete* narrative for searching
\unset ON_ERROR_STOP
drop view v_narrative4search;
\set ON_ERROR_STOP 1

create view v_narrative4search as
-- clin_root_items
select
	vpi.pk_patient as pk_patient,
	vpi.soap_cat as soap_cat,
	vpi.narrative as narrative,
	vpi.pk_item as src_pk,
	vpi.src_table as src_table
from
	v_pat_items vpi
where
	trim(coalesce(vpi.narrative, '')) != ''

union	-- health issues
select
	chi.id_patient as pk_patient,
	'a' as soap_cat,
	chi.description as narrative,
	chi.id as src_pk,
	'clin_health_issue' as src_table
from
	clin_health_issue chi
where
	trim(coalesce(chi.description, '')) != ''

union	-- encounters
select
	cenc.fk_patient as pk_patient,
	's' as soap_cat,
	cenc.description as narrative,
	cenc.id as src_pk,
	'clin_encounter' as src_table
from
	clin_encounter cenc
where
	trim(coalesce(cenc.description, '')) != ''

union	-- episodes
select
	vpep.pk_patient as pk_patient,
	's' as soap_cat,
	vpep.description as narrative,
	vpep.pk_episode as src_pk,
	'clin_episode' as src_table
from
	v_pat_episodes vpep

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
	'hx_family_item' as src_table
from
	v_hx_family vhxf

;

comment on view v_narrative4search is
	'*complete* narrative for patients including
	 health issue/episode/encounter descriptions,
	 mainly for searching the narrative';


-- =============================================
-- complete narrative for display as a journal
\unset ON_ERROR_STOP
drop view v_emr_journal;
\set ON_ERROR_STOP 1

create view v_emr_journal as

-- clin_narrative
select
	vpi.pk_patient as pk_patient,
	cn.modified_when as modified_when,
	cn.clin_when as clin_when,
	case when ((select 1 from v_staff where db_user = cn.modified_by) is null)
		then '<' || cn.modified_by || '>'
		else (select sign from v_staff where db_user = cn.modified_by)
	end as modified_by,
	cn.soap_cat as soap_cat,
	cn.narrative as narrative,
	cn.fk_encounter as pk_encounter,
	cn.fk_episode as pk_episode,
	vpi.pk_health_issue as pk_health_issue,
	cn.pk as src_pk,
	'clin_narrative'::text as src_table
from
	v_pat_items vpi,
	clin_narrative cn
where
	vpi.pk_item = cn.pk_item

union	-- health issues
select
	chi.id_patient as pk_patient,
	chi.modified_when as modified_when,
	chi.modified_when as clin_when,
	case when ((select 1 from v_staff where db_user = chi.modified_by) is null)
		then '<' || chi.modified_by || '>'
		else (select sign from v_staff where db_user = chi.modified_by)
	end as modified_by,
	'a' as soap_cat,
	_('health issue') || ': ' || chi.description as narrative,
	-1 as pk_encounter,
	-1 as pk_episode,
	chi.id as pk_health_issue,
	chi.id as src_pk,
	'clin_health_issue'::text as src_table
from
	clin_health_issue chi

union	-- encounters
select
	cenc.fk_patient as pk_patient,
	cenc.modified_when as modified_when,
	-- FIXME: or last_affirmed ?
	cenc.started as clin_when,
	case when ((select 1 from v_staff where db_user = cenc.modified_by) is null)
		then '<' || cenc.modified_by || '>'
		else (select sign from v_staff where db_user = cenc.modified_by)
	end as modified_by,
	's' as soap_cat,
	_('encounter') || ': ' || cenc.description as narrative,
	cenc.id as pk_encounter,
	-1 as pk_episode,
	-1 as pk_health_issue,
	cenc.id as src_pk,
	'clin_encounter'::text as src_table
from
	clin_encounter cenc
where
	cenc.description is not null

union	-- episodes
select
	vpep.pk_patient as pk_patient,
	vpep.episode_modified_when as modified_when,
	vpep.episode_modified_when as clin_when,
	case when ((select 1 from v_staff where db_user = vpep.episode_modified_by) is null)
		then '<' || vpep.episode_modified_by || '>'
		else (select sign from v_staff where db_user = vpep.episode_modified_by)
	end as modified_by,
	's' as soap_cat,
	_('episode') || ': ' || vpep.description as narrative,
	-1 as pk_encounter,
	vpep.pk_episode as pk_episode,
	-1 as pk_health_issue,
	vpep.pk_episode as src_pk,
	'clin_episode'::text as src_table
from
	v_pat_episodes vpep

union	-- family history
select
	vhxf.pk_patient as pk_patient,
	vhxf.modified_when as modified_when,
	vhxf.clin_when as clin_when,
	case when ((select 1 from v_staff where db_user = vhxf.modified_by) is null)
		then '<' || vhxf.modified_by || '>'
		else (select sign from v_staff where db_user = vhxf.modified_by)
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
	'hx_family_item'::text as src_table
from
	v_hx_family vhxf

union	-- vaccinations
select
	vpv4i.pk_patient as pk_patient,
	vpv4i.modified_when as modified_when,
	vpv4i.date as clin_when,
	case when ((select 1 from v_staff where db_user = vpv4i.modified_by) is null)
		then '<' || vpv4i.modified_by || '>'
		else (select sign from v_staff where db_user = vpv4i.modified_by)
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
	v_pat_vacc4ind vpv4i

union -- allergies
select
	vpa.pk_patient as pk_patient,
	vpa.modified_when as modified_when,
	vpa.date as clin_when,
	case when ((select 1 from v_staff where db_user = vpa.modified_by) is null)
		then '<' || vpa.modified_by || '>'
		else (select sign from v_staff where db_user = vpa.modified_by)
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
	'allergy' as src_table
from
	v_pat_allergies vpa

union	-- lab requests
select
	vlr.pk_patient as pk_patient,
	vlr.modified_when as modified_when,
	vlr.sampled_when as clin_when,
	case when ((select 1 from v_staff where db_user = vlr.modified_by) is null)
		then '<' || vlr.modified_by || '>'
		else (select sign from v_staff where db_user = vlr.modified_by)
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
	v_lab_requests vlr

union	-- test results
select
	vtr.pk_patient as pk_patient,
	vtr.modified_when as modified_when,
	vtr.clin_when as clin_when,
	case when ((select 1 from v_staff where db_user = vtr.modified_by) is null)
		then '<' || vtr.modified_by || '>'
		else (select sign from v_staff where db_user = vtr.modified_by)
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
	v_test_results vtr
;

comment on view v_emr_journal is
	'patient narrative including health issue/episode/
	 encounter descriptions, mainly for display as a journal';

-- =============================================
-- tables
GRANT SELECT, INSERT, UPDATE, DELETE ON
	clin_health_issue
	, clin_health_issue_id_seq
	, clin_episode
	, clin_episode_pk_seq
	, last_act_episode
	, last_act_episode_id_seq
	, encounter_type
	, encounter_type_pk_seq
	, clin_encounter
	, clin_encounter_id_seq
	, curr_encounter
	, curr_encounter_id_seq
	, clin_root_item
	, clin_root_item_pk_item_seq
	, clin_item_type
	, clin_item_type_pk_seq
	, lnk_type2item
	, lnk_type2item_pk_seq
	, clin_narrative
	, clin_narrative_pk_seq
	, lnk_code2narr
	, lnk_code2narr_pk_seq
	, clin_hx_family
	, clin_hx_family_pk_seq
	, clin_diag
	, clin_diag_pk_seq
	, clin_aux_note
	, clin_aux_note_pk_seq
	, _enum_allergy_type
	, _enum_allergy_type_id_seq
	, allergy
	, allergy_id_seq
	, allergy_state
	, allergy_state_id_seq
	, vaccination
	, vaccination_id_seq
	, vaccine
	, vaccine_id_seq
	, vacc_def
	, vacc_def_id_seq
	, vacc_regime
	, vacc_regime_id_seq
	, lnk_pat2vacc_reg
	, lnk_pat2vacc_reg_pk_seq
	, xlnk_identity
	, xlnk_identity_pk_seq
	, form_instances
	, form_instances_pk_seq
	, form_data
	, form_data_pk_seq
	, referral
	, referral_id_seq
	, clin_medication
	, clin_medication_pk_seq
	, constituent
	, soap_cat_ranks
TO GROUP "gm-doctors";

-- measurements
grant select, insert, update, delete on
	test_org
	, test_org_pk_seq
	, test_type
	, test_type_pk_seq
	, test_type_unified
	, test_type_unified_pk_seq
	, lnk_ttype2unified_type
	, lnk_ttype2unified_type_pk_seq
	, lnk_tst2norm
	, lnk_tst2norm_id_seq
	, test_result
	, test_result_pk_seq
	, lab_request
	, lab_request_pk_seq
	, lnk_result2lab_req
	, lnk_result2lab_req_pk_seq
to group "gm-doctors";

-- views
grant select on
	v_pat_encounters
	, v_pat_episodes
	, v_pat_narrative
	, v_pat_items
	, v_pat_allergies
	, v_vacc_regimes
	, v_vacc_defs4reg
	, v_vacc_regs4pat
	, v_vaccs_scheduled4pat
	, v_pat_vacc4ind
	, v_pat_missing_vaccs
	, v_pat_missing_boosters
	, v_most_recent_encounters
	, v_test_type_unified
	, v_unified_test_types
	, v_test_results
	, v_lab_requests
	, v_results4lab_req
	, v_test_org_profile
	, v_pat_diag
	, v_pat_diag_codes
	, v_codes4diag
	, v_pat_rfe
	, v_pat_aoe
	, v_pat_item_types
	, v_types4item
	, v_problem_list
	, v_narrative4search
	, v_emr_journal
	, v_hx_family
to group "gm-doctors";

-- =============================================
-- do simple schema revision tracking
\unset ON_ERROR_STOP
delete from gm_schema_revision where filename='$RCSfile: gmClinicalViews.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmClinicalViews.sql,v $', '$Revision: 1.138 $');

-- =============================================
-- $Log: gmClinicalViews.sql,v $
-- Revision 1.138  2005-04-03 20:14:04  ncq
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
