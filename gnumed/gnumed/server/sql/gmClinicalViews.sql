-- project: GnuMed

-- purpose: views for easier clinical data access
-- author: Karsten Hilbert
-- license: GPL (details at http://gnu.org)

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmClinicalViews.sql,v $
-- $Id: gmClinicalViews.sql,v 1.104 2004-09-25 13:25:56 ncq Exp $

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
	cle.fk_type as pk_type
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

\unset ON_ERROR_STOP
drop index idx_episode_issue;
drop index idx_episode_valid_issue;
create index idx_episode_valid_issue on clin_episode(fk_health_issue) where fk_health_issue is not None;
\set ON_ERROR_STOP 1
create index idx_episode_issue on clin_episode(fk_health_issue);

\unset ON_ERROR_STOP
drop view v_pat_episodes cascade;
drop view v_pat_episodes;
\set ON_ERROR_STOP 1

create view v_pat_episodes as
select
	cep.fk_patient as id_patient,
	cep.description as description,
	cep.is_active as episode_active,
	cep.clinically_relevant as episode_clinically_relevant,
	null as health_issue,
	null as issue_active,
	null as issue_clinically_relevant,
	cep.pk as pk_episode,
	null as pk_health_issue,
	cep.modified_when as episode_modified_when
from
	clin_episode cep
where
	cep.fk_health_issue is null

		union

select
	chi.id_patient as id_patient,
	case when cep.description is null
		then chi.description
		else cep.description
	end as description,
	cep.is_active as episode_active,
	cep.clinically_relevant as episode_clinically_relevant,
	chi.description as health_issue,
	chi.is_active as issue_active,
	chi.clinically_relevant as issue_clinically_relevant,
	cep.pk as pk_episode,
	cep.fk_health_issue as pk_health_issue,
	cep.modified_when as episode_modified_when
from
	clin_episode cep, clin_health_issue chi
where
	-- this should exclude all fk_health_issue=Null ?
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
	select into patient_id id_patient
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
drop rule clin_ritem_no_ins on clin_root_item cascade;
drop rule clin_ritem_no_ins;
drop rule clin_ritem_no_upd on clin_root_item cascade;
drop rule clin_ritem_no_upd;
drop rule clin_ritem_no_del on clin_root_item cascade;
drop rule clin_ritem_no_del;
\set ON_ERROR_STOP 1

-- FIXME: those should actually use PL/pgSQL and raise
--        an exception...
create rule clin_ritem_no_ins as
	on insert to clin_root_item
	do instead nothing;

create rule clin_ritem_no_upd as
	on update to clin_root_item
	do instead nothing;

create rule clin_ritem_no_del as
	on delete to clin_root_item
	do instead nothing;

-- ---------------------------------------------
\unset ON_ERROR_STOP
drop view v_patient_items;
\set ON_ERROR_STOP 1

create view v_patient_items as
select
	extract(epoch from cri.clin_when) as age,
	cri.modified_when as modified_when,
	cri.modified_by as modified_by,
	cri.clin_when as clin_when,
	case cri.row_version
		when 0 then false
		else true
	end as is_modified,
	vpep.id_patient as id_patient,
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
-- tests stuff

\unset ON_ERROR_STOP
drop view v_lab_requests;
\set ON_ERROR_STOP 1

create view v_lab_requests as
select
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
	lr.pk_item as pk_item
from
	lab_request lr,
	test_org torg
where
	lr.fk_test_org=torg.pk
;


\unset ON_ERROR_STOP
drop view v_test_org_profile;
\set ON_ERROR_STOP 1

create view v_test_org_profile as
select
	torg.pk as pk_test_org,
	torg.internal_name,
	ttl.id as pk_test_type,
	ttl.code as test_code,
	ttl.coding_system,
	ttl.local_code as unified_code,
	ttl.name as test_name,
	ttl.local_name as unified_name,
	ttl.basic_unit,
	ttl.comment as test_comment,
	torg.comment as org_comment,
	torg.fk_org as pk_org
from
	test_org torg,
	(test_type tt1 left outer join test_type_local ttl1 on (tt1.id=ttl1.fk_test_type)) ttl
where
	ttl.fk_test_org=torg.pk
;


\unset ON_ERROR_STOP
drop view v_results4lab_req;
\set ON_ERROR_STOP 1

create view v_results4lab_req as
select
	vpep.id_patient as pk_patient,
	tr0.id as pk_result,
	lr.clin_when as req_when,			-- FIXME: should be sampled_when
	lr.lab_rxd_when,
	tr0.clin_when as val_when,
	lr.results_reported_when as reported_when,
	coalesce(ttl0.local_code, ttl0.code) as unified_code,
	coalesce(ttl0.local_name, ttl0.name) as unified_name,
	ttl0.code as lab_code,
	ttl0.name as lab_name,
	case when coalesce(trim(both from tr0.val_alpha), '') = ''
		then tr0.val_num::text
		else case when tr0.val_num is null
			then tr0.val_alpha
			else tr0.val_num::text || ' (' || tr0.val_alpha || ')'
		end
	end as unified_val,
	tr0.val_num,
	tr0.val_alpha,
	tr0.val_unit,
	coalesce(tr0.narrative, '') as progress_note_result,
	coalesce(lr.narrative, '') as progress_note_request,
	tr0.val_normal_range,
	tr0.val_normal_min,
	tr0.val_normal_max,
	tr0.val_target_range,
	tr0.val_target_min,
	tr0.val_target_max,
	tr0.technically_abnormal as abnormal,
	tr0.clinically_relevant as relevant,
	tr0.note_provider,
	lr.request_status as request_status,
	tr0.norm_ref_group as ref_group,
	lr.request_id,
	lr.lab_request_id,
	tr0.material,
	tr0.material_detail,
	tr0.reviewed_by_clinician as reviewed,
	tr0.fk_reviewer as pk_reviewer,
	tr0.fk_type as pk_test_type,
	lr.pk as pk_request,
	lr.fk_test_org as pk_test_org,
	lr.fk_requestor as pk_requestor,
	vpep.pk_health_issue as pk_health_issue,
	tr0.fk_episode as pk_episode,
	tr0.fk_encounter as pk_encounter
from
	(lnk_result2lab_req lr2lr inner join test_result tr1 on (lr2lr.fk_result=tr1.id)) tr0
		inner join
	lab_request lr on (tr0.fk_request=lr.pk),
	v_pat_episodes vpep,
	(test_type tt1 left outer join test_type_local ttl1 on (tt1.id=ttl1.fk_test_type)) ttl0
where
	vpep.pk_episode=lr.fk_episode
		and
	ttl0.id=tr0.fk_type
;

-- ==========================================================
--\unset ON_ERROR_STOP
--drop view v_pending_lab_reqs;
--\set ON_ERROR_STOP 1

-- this isn't very useful due to clinical and demographics
-- being separate services
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
	a.id as id,
	a.pk_item as pk_item,
	vpep.id_patient as id_patient,
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
	a.id_type as id_type,
	a.clin_when as date,
	vpep.pk_health_issue as pk_health_issue,
	a.fk_episode as pk_episode,
	a.fk_encounter as pk_encounter
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
drop view v_vacc_regimes;
\set ON_ERROR_STOP 1

create view v_vacc_regimes as
select
	vreg.id as pk_regime,
	vind.description as indication,
	_(vind.description) as l10n_indication,
	vreg.name as regime,
	coalesce(vreg.comment, '') as comment,
	vreg.fk_indication as pk_indication,
	vreg.fk_recommended_by as pk_recommended_by
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
	v.fk_encounter as pk_encounter
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
		else ((select identity.dob from identity where identity.id=vvs4p.pk_patient) + vvs4p.age_due_max)
	end as latest_due,
	-- note that ...
	-- ... 1) time_left ...
	case when vvs4p.age_due_max is null
		then coalesce(vvs4p.min_interval, vvs4p.age_due_min)
		else (((select identity.dob from identity where identity.id=vvs4p.pk_patient) + vvs4p.age_due_max) - now())
	end as time_left,
	-- ... and 2) amount_overdue ...
	case when vvs4p.age_due_max is null
		then coalesce(vvs4p.min_interval, vvs4p.age_due_min)
		else (now() - ((select identity.dob from identity where identity.id=vvs4p.pk_patient) + vvs4p.age_due_max))
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
	vpi.id_patient as pk_patient,
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
	cn.fk_episode as pk_episode
from
	clin_diag cd,
	clin_narrative as cn,
	v_patient_items vpi
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
	vpi.id_patient as pk_patient,
	cn.pk as pk_narrative,
	cn.clin_when as clin_when,
	cn.soap_cat as soap_cat,
	cn.narrative as rfe,
	cn.fk_encounter as pk_encounter,
	cn.fk_episode as pk_episode,
	cn.pk_item as pk_item
from
	clin_narrative cn,
	v_patient_items vpi
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
	vpi.id_patient as pk_patient,
	cn.pk as pk_narrative,
	cn.clin_when as clin_when,
	cn.soap_cat as soap_cat,
	cn.narrative as aoe,
	cn.fk_encounter as pk_encounter,
	cn.fk_episode as pk_episode,
	cn.pk_item as pk_item
from
	clin_narrative cn,
	v_patient_items vpi
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
	vpi.id_patient as pk_patient,
	cn.clin_when as date,
	cn.soap_cat as soap_cat,
	cn.narrative as narrative,
	cn.is_aoe as is_aoe,
	cn.is_rfe as is_rfe,
	cn.pk_item as pk_item,
	cn.pk as pk_narrative,
	vpi.pk_health_issue as pk_health_issue,
	cn.fk_episode as pk_episode,
	cn.fk_encounter as pk_encounter
from
	clin_narrative cn,
	v_patient_items vpi
where
	cn.pk_item = vpi.pk_item
;

comment on view v_pat_narrative is
	'patient SOAP narrative';


-- *complete* narrative for searching
\unset ON_ERROR_STOP
drop view v_compl_narrative;
\set ON_ERROR_STOP 1

create view v_compl_narrative as
-- soap items
select
	vpi.id_patient as pk_patient,
	cn.soap_cat as soap_cat,
	cn.narrative as narrative,
	cn.pk as src_pk,
	vpi.src_table as src_table
from
	clin_narrative cn,
	v_patient_items vpi
where
	cn.pk_item = vpi.pk_item
		and
	trim(coalesce(cn.narrative, '')) != ''

		union
-- health issues
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

		union
-- episodes
select
	vpep.id_patient as pk_patient,
	'a' as soap_cat,
	vpep.description as narrative,
	vpep.pk_episode as src_pk,
	'clin_episode' as src_table
from
	v_pat_episodes vpep
where
	trim(coalesce(vpep.description, '')) != ''

		union
-- encounters
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
;

comment on view v_compl_narrative is
	'*complete* narrative for patients including
	 health issue/episode/encounter descriptions,
	 mainly for searching the narrative';

-- =============================================
-- types of clin_root_item
\unset ON_ERROR_STOP
drop view v_pat_item_types;
\set ON_ERROR_STOP 1

create view v_pat_item_types as
select
	items.pk_item as pk_item,
	items.id_patient as pk_patient,
	items.code as code,
	items.narrative as narrative,
	items.type as type
from
	((v_patient_items vpi inner join lnk_type2item lt2i on (vpi.pk_item=lt2i.fk_item)) lnkd_items
		inner join clin_item_type cit on (lnkd_items.fk_type=cit.pk)) items
;

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
	((v_patient_items vpi inner join lnk_type2item lt2i on (vpi.pk_item=lt2i.fk_item)) lnkd_items
		inner join clin_item_type cit on (lnkd_items.fk_type=cit.pk)) items
;

-- =============================================
-- problem list

\unset ON_ERROR_STOP
drop view v_problem_list;
\set ON_ERROR_STOP 1

create view v_problem_list as
select
	cep.fk_patient as pk_patient,
	cep.description as problem,
	cep.is_active as is_active,
	cep.clinically_relevant as clinically_relevant,
	cep.pk as pk_episode,
	null as pk_health_issue
from
	clin_episode cep
where
	cep.fk_health_issue is null

		union

select
	chi.id_patient as pk_patient,
	chi.description as problem,
	chi.is_active as is_active,
	chi.clinically_relevant as clinically_relevant,
	null as pk_episode,
	chi.id as pk_health_issue
from
	clin_health_issue chi
;

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
--	, lnk_vacc2vacc_def
--	, lnk_vacc2vacc_def_pk_seq
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
TO GROUP "gm-doctors";

-- measurements
grant select, insert, update, delete on
	test_org
	, test_org_pk_seq
	, test_type
	, test_type_id_seq
	, test_type_local
	, test_type_local_pk_seq
	, lnk_tst2norm
	, lnk_tst2norm_id_seq
	, test_result
	, test_result_id_seq
	, lab_request
	, lab_request_pk_seq
	, lnk_result2lab_req
	, lnk_result2lab_req_pk_seq
to group "gm-doctors";

-- views
GRANT SELECT ON
	v_pat_encounters
	, v_pat_episodes
	, v_pat_narrative
	, v_patient_items
	, v_pat_allergies
	, v_vacc_regimes
	, v_vacc_defs4reg
	, v_vacc_regs4pat
	, v_vaccs_scheduled4pat
	, v_pat_vacc4ind
	, v_pat_missing_vaccs
	, v_pat_missing_boosters
	, v_most_recent_encounters
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
	, v_compl_narrative
TO GROUP "gm-doctors";

-- =============================================
-- do simple schema revision tracking
\unset ON_ERROR_STOP
delete from gm_schema_revision where filename='$RCSfile: gmClinicalViews.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmClinicalViews.sql,v $', '$Revision: 1.104 $');

-- =============================================
-- $Log: gmClinicalViews.sql,v $
-- Revision 1.104  2004-09-25 13:25:56  ncq
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
