-- Project: GNUmed - vaccination related dynamic relations
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmClin-Vaccination-dynamic.sql,v $
-- $Revision: 1.3 $
-- license: GPL
-- author: Ian Haywood, Karsten Hilbert, Richard Terry

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ============================================
-- vacc_indication --
select audit.add_table_for_audit('clin', 'vacc_indication');

comment on table clin.vacc_indication is
	'definition of indications for vaccinations';
comment on column clin.vacc_indication.description is
	'description of indication, eg "Measles",
	 note that this does not have to be a scientific
	 diagnosis, it is simply intended to be an agreed-upon,
	 medically-comprehensible unique identifier for
	 the indication';

-- vacc_route --
select audit.add_table_for_audit('clin', 'vacc_route');

comment on table clin.vacc_route is
	'definition of route via which vaccine is given,
	 currently i.m. and p.o. only but may include
	 "via genetically engineered food" etc in the
	 future';

-- vaccine --
select audit.add_table_for_audit('clin', 'vaccine');

comment on table clin.vaccine is
	'definition of a vaccine as available on the market';
comment on column clin.vaccine.id_route is
	'route this vaccine is given';
comment on column clin.vaccine.trade_name is
	'full name the vaccine is traded under';
comment on column clin.vaccine.short_name is
	'common, maybe practice-specific shorthand name
	 for referring to this vaccine';
comment on column clin.vaccine.is_live is
	'whether this is a live vaccine';
comment on column clin.vaccine.min_age is
	'minimum age this vaccine is licensed for according to the information by the manufacturer';
comment on column clin.vaccine.max_age is
	'maximum age this vaccine is licensed for according to the information
	 by the manufacturer, use "5555 years" to indicate "no maximum age"';

-- clin.vaccine_batches --
comment on column clin.vaccine_batches.batch_no is
	'serial # of a batch of a given vaccine that
	 is awaiting usage in the fridge';

-- clin.lnk_vaccine2inds --
comment on table clin.lnk_vaccine2inds is
	'links vaccines to their indications';

-- clin.vacc_regime --
select audit.add_table_for_audit('clin', 'vacc_regime');

comment on table clin.vacc_regime is
	'holds vaccination schedules/regimes/target diseases';
comment on column clin.vacc_regime.fk_recommended_by is
	'organization recommending this vaccination';
comment on column clin.vacc_regime.fk_indication is
	'vaccination indication this regime is targeted at';
comment on column clin.vacc_regime.name is
	'regime name: schedule/disease/target bacterium...';
comment on column clin.vacc_regime.is_active is
	'whether this schedule is active or not,
	 if False: do not *start* patients on this schedule';

-- clin.lnk_pat2vacc_reg --
select audit.add_table_for_audit('clin', 'lnk_pat2vacc_reg');
-- select add_table_for_notifies('lnk_pat2vacc_reg', 'vacc');

comment on table clin.lnk_pat2vacc_reg is
	'links patients to vaccination regimes they are actually on,
	 this allows for per-patient selection of regimes to be
	 followed, eg. children at different ages may be on different
	 vaccination schedules or some people are on a schedule due
	 to a trip abroad while most others are not';

-- clin.vacc_def --
select audit.add_table_for_audit('clin', 'vacc_def');

comment on table clin.vacc_def is
	'defines a given vaccination event for a particular regime';
comment on column clin.vacc_def.fk_regime is
	'regime to which this event belongs';
comment on column clin.vacc_def.is_booster is
	'does this definition represent a booster,
	 also set for quasi-booster regimes such as
	 Influenza';
comment on column clin.vacc_def.seq_no is
	'sequence number for this vaccination event
	 within a particular schedule/regime,
	 NULL if (is_booster == true)';
comment on column clin.vacc_def.min_age_due is
	'minimum age at which this shot is due';
comment on column clin.vacc_def.max_age_due is
	'maximum age at which this shot is due,
	 if max_age_due = "5555 years": no maximum age';
comment on column clin.vacc_def.min_interval is
	'if (is_booster == true):
		recommended interval for boostering
	 id (is_booster == false):
	 	minimum interval after previous vaccination,
		NULL if seq_no == 1';

\unset ON_ERROR_STOP
alter table clin.vacc_def
	drop constraint numbered_shot_xor_booster;
alter table clin.vacc_def
	drop constraint sensible_min_interval;
\set ON_ERROR_STOP 1

alter table clin.vacc_def
	add constraint numbered_shot_xor_booster
		check (
			((is_booster is true) and (seq_no is null)) or
			((is_booster is false) and (seq_no > 0))
		);

alter table clin.vacc_def
	add constraint sensible_min_interval
		check (
			((min_interval is null) and (seq_no = 1))
				or
			((min_interval is not null) and (min_interval > '0 seconds'::interval) and (is_booster is true))
				or
			((min_interval is not null) and (min_interval > '0 seconds'::interval) and (seq_no > 1))
		);

\unset ON_ERROR_STOP
drop trigger tr_ins_booster_must_have_base_immunity on clin.vacc_def;
drop trigger tr_upd_booster_must_have_base_immunity on clin.vacc_def;
drop trigger tr_del_booster_must_have_base_immunity on clin.vacc_def;
\set ON_ERROR_STOP 1

-- insert
create or replace function clin.f_ins_booster_must_have_base_immunity()
	returns trigger
	language 'plpgsql' as '
BEGIN
	-- do not worry about non-booster inserts
	if NEW.is_booster is false then
		return NEW;
	end if;
	-- only insert booster def if non-booster def exists
	perform 1 from clin.vacc_def where fk_regime = NEW.fk_regime and seq_no is not null;
	if FOUND then
		return NEW;
	end if;
	raise exception ''Cannot define booster shot for regime [%]. There is no base immunization definition.'', NEW.fk_regime;
	return null;
END;
';

create trigger tr_ins_booster_must_have_base_immunity
	before insert on clin.vacc_def
	for each row execute procedure clin.f_ins_booster_must_have_base_immunity();

-- update
create or replace function clin.f_upd_booster_must_have_base_immunity()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	msg text;
BEGIN
	-- do not worry about non-booster updates
	if NEW.is_booster is false then
		return null;
	end if;
	-- after update to booster still non-booster def available ?
	perform 1 from clin.vacc_def where fk_regime = NEW.fk_regime and seq_no is not null;
	if FOUND then
		return null;
	end if;
	msg := ''Cannot set vacc def ['' || NEW.pk || ''] to booster for regime ['' || NEW.fk_regime || '']. There would be no base immunization definition left.'';
	raise exception ''%'', msg;
	return null;
END;';

create trigger tr_upd_booster_must_have_base_immunity
	after update on clin.vacc_def
	for each row execute procedure clin.f_upd_booster_must_have_base_immunity();

-- delete
create or replace function clin.f_del_booster_must_have_base_immunity()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	msg text;
BEGIN
	-- do not worry about booster deletes
	if OLD.is_booster then
		return null;
	end if;
	-- any non-booster rows left ?
	perform 1 from clin.vacc_def where fk_regime = OLD.fk_regime and seq_no is not null;
	if FOUND then
		return null;
	end if;
	-- *any* rows left ?
	perform 1 from clin.vacc_def where fk_regime = OLD.fk_regime;
	if not FOUND then
		-- no problem
		return null;
	end if;
	-- any remaining rows can only be booster rows - which is a problem
	msg := ''Cannot delete last non-booster vacc def ['' || OLD.pk || ''] from regime ['' || OLD.fk_regime || '']. There would be only booster definitions left.'';
	raise exception ''%'', msg;
	return null;
END;';

create trigger tr_del_booster_must_have_base_immunity
	after delete on clin.vacc_def
	for each row execute procedure clin.f_del_booster_must_have_base_immunity();

-- clin.vaccination --
select audit.add_table_for_audit('clin', 'vaccination');
select add_table_for_notifies('clin', 'vaccination', 'vacc');

comment on table clin.vaccination is
	'holds vaccinations actually given';

-- clin.vacc_regime_constraint --
select audit.add_table_for_audit('clin', 'vacc_regime_constraint');

comment on table clin.vacc_regime_constraint is
	'holds constraints which apply to a vaccination schedule';

-- clin.lnk_constraint2vacc_reg --
select audit.add_table_for_audit('clin', 'lnk_constraint2vacc_reg');

comment on table clin.lnk_constraint2vacc_reg is
	'links constraints to schedules';

-- views --
\unset ON_ERROR_STOP
drop view clin.v_vaccine cascade;
\set ON_ERROR_STOP 1

create view clin.v_vaccine as
select
	v.pk as pk_vaccine,
	v.trade_name,
	v.short_name,
	vr.abbreviation as route_abbreviation,
	vr.description as route_description,
	_(vr.description) as l10n_route_description,
	v.is_live,
	v.min_age,
	v.max_age,
	v.comment,
	v.id_route as pk_route
from
	clin.vaccine v,
	clin.vacc_route vr
where
	v.id_route = vr.id
;

comment on view clin.v_vaccine is
	'denormalized data about vaccines';

--
\unset ON_ERROR_STOP
drop view clin.v_inds4vaccine cascade;
\set ON_ERROR_STOP 1

create view clin.v_inds4vaccine as
select
	v.trade_name,
	v.short_name,
	i.description as indication,
	_(i.description) as l10n_indication,
	v.is_live,
	v.min_age,
	v.max_age,
	v.comment,
	v.pk as pk_vaccine,
	v.id_route as pk_route,
	i.id as pk_vacc_indication
from
	clin.vaccine v,
	clin.vacc_indication i,
	clin.lnk_vaccine2inds lv2i
where
	v.pk = lv2i.fk_vaccine and
	i.id = lv2i.fk_indication
;

comment on view clin.v_inds4vaccine is
	'lists indications for vaccines';


\unset ON_ERROR_STOP
drop view clin.v_vacc_regimes cascade;
\set ON_ERROR_STOP 1

create view clin.v_vacc_regimes as
select
	vreg.id as pk_regime,
	vind.description as indication,
	_(vind.description) as l10n_indication,
	vreg.name as regime,
	(select max(vdef.seq_no) from clin.vacc_def vdef where vreg.id = vdef.fk_regime)
		as shots,
	coalesce(vreg.comment, '') as comment,
	(select vdef.min_age_due from clin.vacc_def vdef where vreg.id = vdef.fk_regime and vdef.seq_no=1)
		as min_age_due,
	vreg.is_active as is_active,
	vreg.fk_indication as pk_indication,
	vreg.fk_recommended_by as pk_recommended_by,
	vreg.xmin as xmin_vacc_regime
from
	clin.vacc_regime vreg,
	clin.vacc_indication vind
where
	vreg.fk_indication = vind.id
;

comment on view clin.v_vacc_regimes is
	'all vaccination schedules known to the system';

-- -----------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_vacc_defs4reg cascade;
\set ON_ERROR_STOP 1

create view clin.v_vacc_defs4reg as
select
	vreg.id as pk_regime,
	vind.description as indication,
	_(vind.description) as l10n_indication,
	vreg.name as regime,
	coalesce(vreg.comment, '') as reg_comment,
	vreg.is_active as is_active,
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
	clin.vacc_regime vreg,
	clin.vacc_indication vind,
	clin.vacc_def vdef
where
	vreg.id = vdef.fk_regime
		and
	vreg.fk_indication = vind.id
order by
	indication,
	vacc_seq_no
;

comment on view clin.v_vacc_defs4reg is
	'vaccination event definitions for all schedules known to the system';

-- -----------------------------------------------------
create view clin.v_vacc_regs4pat as
select
	lp2vr.fk_patient as pk_patient,
	vvr.indication as indication,
	vvr.l10n_indication as l10n_indication,
	vvr.regime as regime,
	vvr.comment as comment,
	vvr.is_active as is_active,
	vvr.pk_regime as pk_regime,
	vvr.pk_indication as pk_indication,
	vvr.pk_recommended_by as pk_recommended_by
from
	clin.lnk_pat2vacc_reg lp2vr,
	clin.v_vacc_regimes vvr
where
	vvr.pk_regime = lp2vr.fk_regime
;

comment on view clin.v_vacc_regs4pat is
	'selection of configured vaccination schedules a patient is actually on';

-- -----------------------------------------------------
create view clin.v_vaccs_scheduled4pat as
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
	clin.v_vacc_regs4pat vvr4p,
	clin.v_vacc_defs4reg vvd4r
where
	vvd4r.pk_regime = vvr4p.pk_regime
;

comment on view clin.v_vaccs_scheduled4pat is
	'vaccinations scheduled for a patient according
	 to the vaccination schedules he/she is on';

-- -----------------------------------------------------
create view clin.v_pat_vacc4ind as
select
	v.fk_patient as pk_patient,
	v.id as pk_vaccination,
	v.clin_when as date,
	vi4v.indication,
	vi4v.l10n_indication,
	vi4v.trade_name as vaccine,
	vi4v.short_name as vaccine_short,
	v.batch_no as batch_no,
	v.site as site,
	coalesce(v.narrative, '') as narrative,
	vi4v.pk_vacc_indication as pk_indication,
	v.fk_provider as pk_provider,
	vi4v.pk_vaccine as pk_vaccine,
	vpep.pk_health_issue as pk_health_issue,
	v.fk_episode as pk_episode,
	v.fk_encounter as pk_encounter,
	v.modified_when as modified_when,
	v.modified_by as modified_by,
	v.xmin as xmin_vaccination
from
	clin.vaccination v,
--	clin.vaccine vcine,
--	clin.lnk_vaccine2inds lv2i,
	clin.v_inds4vaccine vi4v,
--	clin.vacc_indication vind,
	clin.v_pat_episodes vpep
where
	vpep.pk_episode=v.fk_episode
		and
--	v.fk_vaccine = vcine.pk
	v.fk_vaccine = vi4v.pk_vaccine
--		and
--	lv2i.fk_vaccine = vcine.pk
--		and
--	lv2i.fk_indication = vind.id
;

comment on view clin.v_pat_vacc4ind is
	'vaccinations a patient has actually received for the various
	 indications, we operate under the assumption that every shot
	 given counts toward base immunisation, eg. all shots are valid';

-- -----------------------------------------------------
create view clin.v_pat_missing_vaccs as
select
	vvs4p.pk_patient,
	vvs4p.indication,
	vvs4p.l10n_indication,
	vvs4p.regime,
	vvs4p.reg_comment,
	vvs4p.vacc_seq_no as seq_no,
	case when vvs4p.age_due_max is null
		then (now() + coalesce(vvs4p.min_interval, vvs4p.age_due_min))
		else ((select dem.identity.dob from dem.identity where dem.identity.pk=vvs4p.pk_patient) + vvs4p.age_due_max)
	end as latest_due,
	-- note that ...
	-- ... 1) time_left ...
	case when vvs4p.age_due_max is null
		then coalesce(vvs4p.min_interval, vvs4p.age_due_min)
		else (((select dem.identity.dob from dem.identity where dem.identity.pk=vvs4p.pk_patient) + vvs4p.age_due_max) - now())
	end as time_left,
	-- ... and 2) amount_overdue ...
	case when vvs4p.age_due_max is null
		then coalesce(vvs4p.min_interval, vvs4p.age_due_min)
		else (now() - ((select dem.identity.dob from dem.identity where dem.identity.pk=vvs4p.pk_patient) + vvs4p.age_due_max))
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
	clin.v_vaccs_scheduled4pat vvs4p
where
	vvs4p.is_booster is false
		and
	vvs4p.vacc_seq_no > (
		select count(*)
		from clin.v_pat_vacc4ind vpv4i
		where
			vpv4i.pk_patient = vvs4p.pk_patient
				and
			vpv4i.indication = vvs4p.indication
	)
;

comment on view clin.v_pat_missing_vaccs is
	'vaccinations a patient has not been given yet according
	 to the schedules a patient is on and the previously
	 received vaccinations';

-- -----------------------------------------------------
-- FIXME: only list those that DO HAVE a previous vacc (max(date) is not null)
create view clin.v_pat_missing_boosters as
select
	vvs4p.pk_patient,
	vvs4p.indication,
	vvs4p.l10n_indication,
	vvs4p.regime,
	vvs4p.reg_comment,
	vvs4p.vacc_seq_no as seq_no,
	coalesce(
		((select max(vpv4i11.date)
		  from clin.v_pat_vacc4ind vpv4i11
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
			from clin.v_pat_vacc4ind vpv4i12
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
	clin.v_vaccs_scheduled4pat vvs4p
where
	vvs4p.is_booster is true
		and
	vvs4p.min_interval < age (
		(select max(vpv4i13.date)
			from clin.v_pat_vacc4ind vpv4i13
			where
				vpv4i13.pk_patient = vvs4p.pk_patient
					and
				vpv4i13.indication = vvs4p.indication
		))
;

comment on view clin.v_pat_missing_boosters is
	'boosters a patient has not been given yet according
	 to the schedules a patient is on and the previously
	 received vaccinations';


-- ============================================
GRANT SELECT, INSERT, UPDATE, DELETE ON
	clin.vaccination
	, clin.vaccination_id_seq
	, clin.vaccine
	, clin.vaccine_pk_seq
	, clin.lnk_vaccine2inds
	, clin.lnk_vaccine2inds_id_seq
	, clin.vacc_indication
	, clin.vacc_indication_id_seq
	, clin.vacc_def
	, clin.vacc_def_id_seq
	, clin.vacc_regime
	, clin.vacc_regime_id_seq
	, clin.lnk_pat2vacc_reg
	, clin.lnk_pat2vacc_reg_pk_seq
	, clin.vacc_regime_constraint
	, clin.vacc_regime_constraint_pk_seq
	, clin.lnk_constraint2vacc_reg
	, clin.lnk_constraint2vacc_reg_pk_seq
TO GROUP "gm-doctors";

grant select on
	clin.v_vacc_regimes
	, clin.v_vacc_defs4reg
	, clin.v_vacc_regs4pat
	, clin.v_vaccs_scheduled4pat
	, clin.v_inds4vaccine
	, clin.v_pat_vacc4ind
	, clin.v_pat_missing_vaccs
	, clin.v_pat_missing_boosters
	, clin.v_vaccine
to group "gm-doctors";

-- ===================================================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmClin-Vaccination-dynamic.sql,v $', '$Revision: 1.3 $');

-- ===================================================================
-- $Log: gmClin-Vaccination-dynamic.sql,v $
-- Revision 1.3  2006-02-27 11:24:38  ncq
-- - explain *_age: NULL -> 5555 years
-- - add clin.v_vaccine and improve other views
--
-- Revision 1.2  2006/02/19 13:45:05  ncq
-- - move the rest of the dynamic vacc stuff from gmClinicalViews.sql
--   into gmClin-Vaccination-dynamic.sql
-- - add vaccination schedule constraint enumeration data
-- - add is_active to clin.vacc_regime
-- - add clin.vacc_regime_constraint
-- - add clin.lnk_constraint2vacc_reg
-- - proper grants
--
-- Revision 1.1  2006/02/08 15:15:39  ncq
-- - factor our vaccination stuff into its own set of files
-- - remove clin.lnk_vacc_ind2code in favour of clin.coded_term usage
-- - improve comments as discussed on the list
--
--
