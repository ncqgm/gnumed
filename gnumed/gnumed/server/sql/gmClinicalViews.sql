-- project: GnuMed

-- purpose: views for easier clinical data access
-- author: Karsten Hilbert
-- license: GPL (details at http://gnu.org)

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmClinicalViews.sql,v $
-- $Id: gmClinicalViews.sql,v 1.56 2004-04-26 09:38:43 ncq Exp $

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
\unset ON_ERROR_STOP
drop index idx_item_encounter;
drop index idx_item_episode;
drop index idx_episode_h_issue;
drop index idx_allergy_comment;
\set ON_ERROR_STOP 1

create index idx_item_encounter on clin_root_item(id_encounter);
create index idx_item_episode on clin_root_item(id_episode);
create index idx_episode_h_issue on clin_episode(id_health_issue);

-- =============================================
-- encounters
\unset ON_ERROR_STOP
drop view v_i18n_enum_encounter_type;
\set ON_ERROR_STOP 1

create view v_i18n_enum_encounter_type as
select
	_enum_encounter_type.id as id,
	_(_enum_encounter_type.description) as description
from
	_enum_encounter_type
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
	cle.fk_type as pk_type
from
	clin_encounter cle,
	_enum_encounter_type et
where
	cle.fk_type = et.id
;

-- current ones
\unset ON_ERROR_STOP
drop view v_i18n_curr_encounters;
\set ON_ERROR_STOP 1

create view v_i18n_curr_encounters as
select
	cu_e.id_encounter as pk_encounter,
	cu_e.started as started,
	cu_e.last_affirmed as last_affirmed,
	cu_e.comment as status,
	cl_e.fk_patient as pk_patient,
	cl_e.fk_location as pk_location,
	cl_e.fk_provider as pk_provider,
	_(et.description) as type,
	cl_e.description as description
from
	clin_encounter cl_e,
	_enum_encounter_type et,
	curr_encounter cu_e
where
	et.id = cl_e.fk_type
		and
	cu_e.id_encounter = cl_e.id
;

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
	_enum_encounter_type et
where
	ce1.fk_type = et.id
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
\unset ON_ERROR_STOP
drop view v_pat_episodes;
\set ON_ERROR_STOP 1

create view v_pat_episodes as
select
	chi.id_patient as id_patient,
	cep.id as id_episode,
	cep.description as episode,
	chi.id as id_health_issue,
	chi.description as health_issue
from
	clin_episode cep, clin_health_issue chi
where
	cep.id_health_issue=chi.id
;

-- =============================================
-- clin_root_item stuff
\unset ON_ERROR_STOP
drop trigger TR_clin_item_mod on clin_root_item;
drop function F_announce_clin_item_mod();
\set ON_ERROR_STOP 1

create function F_announce_clin_item_mod() returns opaque as '
declare
	episode_id integer;
	patient_id integer;
begin
	-- get episode ID
	if TG_OP = ''DELETE'' then
		episode_id := OLD.id_episode;
	else
		episode_id := NEW.id_episode;
	end if;
	-- track back to patient ID
	select into patient_id id_patient
		from v_pat_episodes vpep
		where vpep.id_episode = episode_id
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
		execute procedure F_announce_clin_item_mod()
;

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
	cri.pk_item as id_item,
	cri.id_encounter as id_encounter,
	cri.id_episode as id_episode,
	vpep.id_health_issue as id_health_issue,
	cri.narrative as narrative,
	sys.relname as src_table
from
	clin_root_item cri, v_pat_episodes vpep, pg_class sys
where
	vpep.id_episode=cri.id_episode
		and
	cri.tableoid=sys.oid
order by
	age
;

-- ==========================================================
-- tests stuff

--\unset ON_ERROR_STOP
--drop view v_test_result;
--\set ON_ERROR_STOP 1

--create view v_test_result as
--	select
--		tr.id as id_result,
--		vpep.id_patient as id_patient,
--		vpep.id_health_issue as id_health_issue,
--		tr.id_episode as id_episode,
--		tr.id_encounter as id_encounter,
--		tr.fk_type as pk_type,
--		tr.clin_when as result_when,
--		tt.code as test_code,
--		tt.name as test_name,
--		tr.val_num as value_num,
--		tr.val_alpha as value_alpha,
--		tr.val_unit as value_unit,
--		tr.technically_abnormal as technically_abnormal,
--		tr.val_normal_min as normal_min,
--		tr.val_normal_max as normal_max,
--		tr.val_normal_range as normal_range,
--		tr.note_provider as comment_provider,
--		tr.reviewed_by_clinician as reviewed,
--		tr.fk_reviewer as pk_reviewer,
--		tr.clinically_relevant as clinically_relevant,
--		tr.narrative as comment_doc
--	from
--		test_result tr,
--		test_type tt,
--		v_pat_episodes vpep
--	where
--		tr.fk_type = tt.id
--			AND
--		tr.id_episode = vpep.id_episode
--;

\unset ON_ERROR_STOP
drop view v_test_org_profile;
\set ON_ERROR_STOP 1

create view v_test_org_profile as
select
	torg.pk as pk_test_org,
	torg.internal_name,
	tt.id as pk_test_type,
	tt.code as test_code,
	tt.coding_system,
	ttu.internal_code as unified_code,
	tt.name as test_name,
	ttu.internal_name as unified_name,
	tt.basic_unit,
	tt.comment as test_comment,
	torg.comment as org_comment,
	torg.fk_org as pk_org
from
	test_org torg,
	test_type tt,
	test_type_uni ttu
where
	tt.fk_test_org=torg.pk
		and
	ttu.fk_test_type=tt.id
;


\unset ON_ERROR_STOP
drop view v_results4lab_req;
\set ON_ERROR_STOP 1

-- FIXME: refine using merged_test_types
create view v_results4lab_req as
select
	vpep.id_patient as pk_patient,
	tr.id as pk_result,
	lr.clin_when as req_when,
	lr.lab_rxd_when,
	tr.clin_when as val_when,
	lr.results_reported_when as reported_when,
	coalesce(ttu.internal_code, ttu.code) as unified_code,
	coalesce(ttu.internal_name, ttu.name) as unified_name,
	ttu.code as lab_code,
	ttu.name as lab_name,
	case when coalesce(trim(both from tr.val_alpha), '') = ''
		then tr.val_num::text
		else case when tr.val_num is null
			then tr.val_alpha
			else tr.val_num::text || ' (' || tr.val_alpha || ')'
		end
	end as unified_val,
	tr.val_num,
	tr.val_alpha,
	tr.val_unit,
	coalesce(tr.narrative, '') as progress_note_result,
	coalesce(lr.narrative, '') as progress_note_request,
	tr.val_normal_range,
	tr.val_normal_min,
	tr.val_normal_max,
	tr.technically_abnormal as abnormal,
	tr.clinically_relevant as relevant,
	tr.note_provider,
	lr.request_status as request_status,
	tr.norm_ref_group as ref_group,
	lr.request_id,
	lr.lab_request_id,
	tr.material,
	tr.material_detail,
	tr.reviewed_by_clinician as reviewed,
	tr.fk_reviewer as pk_reviewer,
	tr.fk_type as pk_test_type,
	lr.pk as pk_request,
	lr.fk_test_org as pk_test_org,
	lr.fk_requestor as pk_requestor
from
	(lnk_result2lab_req lr2lr inner join test_result tr1 on (lr2lr.fk_result=tr1.id)) tr
		inner join
	lab_request lr on (tr.fk_request=lr.pk),
	v_pat_episodes vpep,
	(test_type tt1 left outer join test_type_uni ttu1 on (tt1.id=ttu1.fk_test_type)) ttu
where
	lr.is_pending=false
		and
	vpep.id_episode=lr.id_episode
		and
	ttu.id=tr.fk_type
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
drop trigger TR_allergy_add_del on allergy;
drop function F_announce_allergy_add_del();
\set ON_ERROR_STOP 1

create function F_announce_allergy_add_del() returns opaque as '
declare
	episode_id integer;
	patient_id integer;
begin
	-- get episode ID
	if TG_OP = ''INSERT'' then
		episode_id := NEW.id_episode;
	else
		episode_id := OLD.id_episode;
	end if;
	-- track back to patient ID
	select into patient_id id_patient
		from v_pat_episodes vpep
		where vpep.id_episode = episode_id
		limit 1;
	-- now, execute() the NOTIFY
	execute ''notify "allergy_add_del_db:'' || patient_id || ''"'';
	return NULL;
end;
' language 'plpgsql';

create trigger TR_allergy_add_del
	after insert or delete
	on allergy
	for each row
		execute procedure F_announce_allergy_add_del()
;
-- should really be "for each statement" but that isn't supported yet by PostgreSQL
-- or maybe not since then we won't be able to separate affected patients in UPDATEs

\unset ON_ERROR_STOP
drop view v_pat_allergies;
\set ON_ERROR_STOP 1

create view v_pat_allergies as
select
	a.id as id,
	a.pk_item as id_item,
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
	vpep.id_health_issue as id_health_issue,
	a.id_episode as id_episode,
	a.id_encounter as id_encounter
from
	allergy a,
	_enum_allergy_type at,
	v_pat_episodes vpep
where
	vpep.id_episode=a.id_episode
		and
	at.id=a.id_type
;

-- ==========================================================
-- vaccination stuff
\unset ON_ERROR_STOP
drop view v_vacc_regimes;
\set ON_ERROR_STOP 1

create view v_vacc_regimes as
select
	vreg.id as pk_regime,
	vind.description as indication,
	vreg.name as regime,
	coalesce(vreg.comment, '') as reg_comment,
	vdef.is_booster as is_booster,
	case when vdef.is_booster
		then 0
		else vdef.seq_no
	end as vacc_seq_no,
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
	vcine.id as pk_vaccine
from
	vaccination v,
	vaccine vcine,
	lnk_vaccine2inds lv2i,
	vacc_indication vind
where
	v.fk_vaccine = vcine.id
		and
	lv2i.fk_vaccine = vcine.id
		and
	lv2i.fk_indication = vind.id
;

\unset ON_ERROR_STOP
drop view v_pat_missing_vaccs;
drop view v_pat_missing_boosters;
\set ON_ERROR_STOP 1

create view v_pat_missing_vaccs as
select
	vpv4i1.pk_patient as pk_patient,
	vvr1.indication as indication,
	vvr1.regime as regime,
	vvr1.reg_comment as reg_comment,
	vvr1.vacc_seq_no as seq_no,
	vvr1.age_due_min as age_due_min,
	vvr1.age_due_max as age_due_max,
	vvr1.min_interval as min_interval,
	vvr1.vacc_comment as vacc_comment,
	vvr1.pk_indication as pk_indication,
	vvr1.pk_recommended_by as pk_recommended_by
from
	v_pat_vacc4ind vpv4i1,
	v_vacc_regimes vvr1
where
	vvr1.is_booster = false
		and
	vvr1.vacc_seq_no > (
		select count(*)
		from v_pat_vacc4ind vpv4i2
		where
			vpv4i2.pk_patient = vpv4i1.pk_patient
				and
			vpv4i2.indication = vvr1.indication
	)
;

create view v_pat_missing_boosters as
select
	vpv4i1.pk_patient as pk_patient,
	vvr1.indication as indication,
	vvr1.regime as regime,
	vvr1.reg_comment as reg_comment,
	vvr1.vacc_seq_no as seq_no,
	vvr1.age_due_min as age_due_min,
	vvr1.age_due_max as age_due_max,
	vvr1.min_interval as min_interval,
	vvr1.vacc_comment as vacc_comment,
	vvr1.pk_indication as pk_indication,
	vvr1.pk_recommended_by as pk_recommended_by
from
	v_pat_vacc4ind vpv4i1,
	v_vacc_regimes vvr1
where
	vvr1.is_booster = true
		and
	vvr1.min_interval < age (
		(select max(vpv4i2.date)
		 from v_pat_vacc4ind vpv4i2
		 where
			vpv4i2.pk_patient = vpv4i1.pk_patient
				and
			vpv4i2.indication = vpv4i1.indication
		)
	)
;
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
	NEW.id_encounter := OLD.id_encounter;
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
GRANT SELECT ON
	clin_root_item,
	clin_health_issue,
	clin_episode,
	last_act_episode,
	_enum_encounter_type,
	clin_encounter,
	curr_encounter,
	clin_note,
	clin_aux_note,
	_enum_hx_type,
	_enum_hx_source,
	clin_history,
	clin_physical,
	_enum_allergy_type,
	allergy,
	vaccination,
	vaccine,
	vacc_def
	, vacc_regime
	, lnk_vacc2vacc_def
	, xlnk_identity
	, form_instances
	, form_data
TO GROUP "gm-doctors";

GRANT SELECT, INSERT, UPDATE, DELETE ON
	"clin_root_item",
	"clin_root_item_pk_item_seq",
	"clin_health_issue",
	"clin_health_issue_id_seq",
	"clin_episode",
	"clin_episode_id_seq",
	"last_act_episode",
	"last_act_episode_id_seq",
	"_enum_encounter_type",
	"_enum_encounter_type_id_seq",
	"clin_encounter",
	"clin_encounter_id_seq",
	"curr_encounter",
	"curr_encounter_id_seq",
	"clin_note",
	"clin_note_id_seq",
	"clin_aux_note",
	"clin_aux_note_id_seq",
	"_enum_hx_type",
	"_enum_hx_type_id_seq",
	"_enum_hx_source",
	"_enum_hx_source_id_seq",
	"clin_history",
	"clin_history_id_seq",
	"clin_physical",
	"clin_physical_id_seq",
	"_enum_allergy_type",
	"_enum_allergy_type_id_seq",
	"allergy",
	"allergy_id_seq",
	"vaccination",
	"vaccination_id_seq",
	"vaccine",
	"vaccine_id_seq"
	, vacc_def
	, vacc_def_id_seq
	, vacc_regime
	, vacc_regime_id_seq
	, lnk_vacc2vacc_def
	, lnk_vacc2vacc_def_pk_seq
	, xlnk_identity
	, xlnk_identity_pk_seq
	, form_instances
	, form_instances_pk_seq
	, form_data
	, form_data_pk_seq
TO GROUP "_gm-doctors";

grant select on
	test_org
	, test_type
	, test_type_uni
	, lnk_tst2norm
	, test_result
	, lab_request
	, lnk_result2lab_req
to group "gm-doctors";

grant select, insert, update, delete on
	test_org
	, test_org_pk_seq
	, test_type
	, test_type_id_seq
	, test_type_uni
	, test_type_uni_pk_seq
	, lnk_tst2norm
	, lnk_tst2norm_id_seq
	, test_result
	, test_result_id_seq
	, lab_request
	, lab_request_pk_seq
	, lnk_result2lab_req
	, lnk_result2lab_req_pk_seq
to group "_gm-doctors";

GRANT SELECT ON
	v_i18n_enum_encounter_type
	, v_pat_encounters
	, v_pat_episodes
	, v_patient_items
	, v_pat_allergies
	, v_vacc_regimes
	, v_pat_vacc4ind
	, v_pat_missing_vaccs
	, v_pat_missing_boosters
	, v_most_recent_encounters
	, v_results4lab_req
	, v_test_org_profile
TO GROUP "gm-doctors";

--GRANT SELECT, INSERT, UPDATE, DELETE ON
--	"v_i18n_enum_encounter_type",
--	"v_pat_episodes",
--	"v_patient_items",
--	"v_i18n_curr_encounters",
--	"v_pat_allergies",
--	"v_vacc_regimes",
--	v_patient_vaccinations,
--	v_pat_due_vaccs,
--	v_pat_overdue_vaccs
--TO GROUP "_gm-doctors";

-- =============================================
-- do simple schema revision tracking
\unset ON_ERROR_STOP
delete from gm_schema_revision where filename='$RCSfile: gmClinicalViews.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmClinicalViews.sql,v $', '$Revision: 1.56 $');

-- =============================================
-- $Log: gmClinicalViews.sql,v $
-- Revision 1.56  2004-04-26 09:38:43  ncq
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
