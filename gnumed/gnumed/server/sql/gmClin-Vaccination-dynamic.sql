-- Project: GNUmed - vaccination related dynamic relations
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmClin-Vaccination-dynamic.sql,v $
-- $Revision: 1.6 $
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
select audit.add_table_for_audit('clin', 'vaccine_batches');

comment on column clin.vaccine_batches.batch_no is
	'serial # of a batch of a given vaccine that
	 is awaiting usage in the fridge';


-- clin.lnk_vaccine2inds --
select audit.add_table_for_audit('clin', 'lnk_vaccine2inds');

comment on table clin.lnk_vaccine2inds is
	'links vaccines to their indications';


-- clin.vaccination_course --
select audit.add_table_for_audit('clin', 'vaccination_course');

comment on table clin.vaccination_course is
	'holds vaccination courses defined at a techno-medical level for
	 a single indication and will in many cases represent a part of
	 a "recommended multi-epitope schedule",
	 note that one organization can indeed recommend several courses
	 for one and the same indication - which then only differ in their
	 constraints, PostgreSQL does not currently offer the best tools
	 to enforce such constraints';
comment on column clin.vaccination_course.fk_recommended_by is
	'the source/organization which defined this course, can be used to
	 differentiate several locale-dependant courses for the same indication
	 and yet tell them apart';
comment on column clin.vaccination_course.fk_indication is
	'vaccination indication this course is targeted at';
comment on column clin.vaccination_course.is_active is
	'whether this course is active or not,
	 if False: do not newly *start* patients on this course';
comment on column clin.vaccination_course.comment is
	'a free-text comment on this vaccination course';


-- -- clin.vaccination_course_constraint --
select audit.add_table_for_audit('clin', 'vaccination_course_constraint');

comment on table clin.vaccination_course_constraint is
	'non-age constraints applying to a certain vaccination course
	 such as "female only", "Torres-Strait-Islander", etc.';
comment on column clin.vaccination_course_constraint.description is
	'description/label/name of the constraint';


-- -- clin.lnk_constraint2vacc_course --
select audit.add_table_for_audit('clin', 'lnk_constraint2vacc_course');

comment on table clin.lnk_constraint2vacc_course is
	'this table actually links constraints to vaccination courses';


-- -- clin.vaccincation_schedule --
select audit.add_table_for_audit('clin', 'vaccination_schedule');

comment on table clin.vaccination_schedule is
	'This table holds schedules as recommended by some authority
	 such as a Vaccination Council. There will be numerous schedules
	 depending on locale, constraints, age group etc. These schedules
	 may be single or multi-epitope depending on their definition.
	 A schedule acts as a convenient handle aggregating possibly several
	 vaccination courses under a common name.';
comment on column clin.vaccination_schedule.name is
	'name of the schedule as defined by some authority';


-- -- clin.lnk_vaccination_course2schedule --
select audit.add_table_for_audit('clin', 'lnk_vaccination_course2schedule');

comment on table clin.lnk_vaccination_course2schedule is
	'this table links vaccination courses for a single epitope
	 into schedules defined and recommended by a vaccination
	 council or similar entity';


-- -- clin.lnk_pat2vaccination_course --
select audit.add_table_for_audit('clin', 'lnk_pat2vaccination_course');
-- select add_table_for_notifies('lnk_pat2vaccination_course', 'vacc');

comment on table clin.lnk_pat2vaccination_course is
	'links patients to vaccination courses they are actually on,
	 this allows for per-patient selection of courses to be
	 followed, eg. children at different ages may be on different
	 vaccination courses or some people are on a course due
	 to a trip abroad while most others are not';


-- -- clin.vaccination_definition --
select audit.add_table_for_audit('clin', 'vaccination_definition');

comment on table clin.vaccination_definition is
	'defines a given vaccination event for a particular course';
comment on column clin.vaccination_definition.fk_course is
	'course to which this event belongs';
comment on column clin.vaccination_definition.is_booster is
	'does this definition represent a booster,
	 also set for quasi-booster courses such as
	 Influenza';
comment on column clin.vaccination_definition.seq_no is
	'sequence number for this vaccination event
	 within a particular course,
	 NULL if (is_booster == true)';
comment on column clin.vaccination_definition.min_age_due is
	'minimum age at which this shot is due';
comment on column clin.vaccination_definition.max_age_due is
	'maximum age at which this shot is due,
	 if max_age_due = "5555 years": no maximum age';
comment on column clin.vaccination_definition.min_interval is
	'if (is_booster == true):
		recommended interval for boostering
	 id (is_booster == false):
	 	minimum interval after previous vaccination,
		NULL if seq_no == 1';

\unset ON_ERROR_STOP
alter table clin.vaccination_definition
	drop constraint numbered_shot_xor_booster;
alter table clin.vaccination_definition
	drop constraint sensible_min_interval;
\set ON_ERROR_STOP 1

alter table clin.vaccination_definition
	add constraint numbered_shot_xor_booster
		check (
			((is_booster is true) and (seq_no is null)) or
			((is_booster is false) and (seq_no > 0))
		);

alter table clin.vaccination_definition
	add constraint sensible_min_interval
		check (
			((min_interval is null) and (seq_no = 1))
				or
			((min_interval is not null) and (min_interval > '0 seconds'::interval) and (is_booster is true))
				or
			((min_interval is not null) and (min_interval > '0 seconds'::interval) and (seq_no > 1))
		);

\unset ON_ERROR_STOP
drop trigger tr_ins_booster_must_have_base_immunity on clin.vaccination_definition;
drop trigger tr_upd_booster_must_have_base_immunity on clin.vaccination_definition;
drop trigger tr_del_booster_must_have_base_immunity on clin.vaccination_definition;
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
	perform 1 from clin.vaccination_definition where fk_course = NEW.fk_course and seq_no is not null;
	if FOUND then
		return NEW;
	end if;
	raise exception ''Cannot define booster shot for course [%]. There is no base immunization definition.'', NEW.fk_course;
	return null;
END;
';

create trigger tr_ins_booster_must_have_base_immunity
	before insert on clin.vaccination_definition
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
	perform 1 from clin.vaccination_definition where fk_course = NEW.fk_course and seq_no is not null;
	if FOUND then
		return null;
	end if;
	msg := ''Cannot set vacc def ['' || NEW.pk || ''] to booster for course ['' || NEW.fk_course || '']. There would be no base immunization definition left.'';
	raise exception ''%'', msg;
	return null;
END;';

create trigger tr_upd_booster_must_have_base_immunity
	after update on clin.vaccination_definition
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
	perform 1 from clin.vaccination_definition where fk_course = OLD.fk_course and seq_no is not null;
	if FOUND then
		return null;
	end if;
	-- *any* rows left ?
	perform 1 from clin.vaccination_definition where fk_course = OLD.fk_course;
	if not FOUND then
		-- no problem
		return null;
	end if;
	-- any remaining rows can only be booster rows - which is a problem
	msg := ''Cannot delete last non-booster vacc def ['' || OLD.pk || ''] from course ['' || OLD.fk_course || '']. There would be only booster definitions left.'';
	raise exception ''%'', msg;
	return null;
END;';

create trigger tr_del_booster_must_have_base_immunity
	after delete on clin.vaccination_definition
	for each row execute procedure clin.f_del_booster_must_have_base_immunity();

-- clin.vaccination --
select audit.add_table_for_audit('clin', 'vaccination');
select add_table_for_notifies('clin', 'vaccination', 'vacc');

comment on table clin.vaccination is
	'holds vaccinations actually given';

-- clin.vaccination_course_constraint --
select audit.add_table_for_audit('clin', 'vaccination_course_constraint');

comment on table clin.vaccination_course_constraint is
	'holds constraints which apply to a vaccination course';

-- clin.lnk_constraint2vacc_course --
select audit.add_table_for_audit('clin', 'lnk_constraint2vacc_course');

comment on table clin.lnk_constraint2vacc_course is
	'links constraints to courses';

-- -----------------------------------------------------------------------
-- -- views --
-- -----------------------------------------------------------------------
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
drop view clin.v_vaccination_courses cascade;
\set ON_ERROR_STOP 1

create view clin.v_vaccination_courses as
select
	vcourse.pk as pk_course,
	vind.description as indication,
	_(vind.description) as l10n_indication,
	(select name_long from ref_source where ref_source.pk = vcourse.fk_recommended_by)
		as recommended_by_name_long,
	(select name_short from ref_source where ref_source.pk = vcourse.fk_recommended_by)
		as recommended_by_name_short,
	(select version from ref_source where ref_source.pk = vcourse.fk_recommended_by)
		as recommended_by_version,
	(select max(vdef.seq_no) from clin.vaccination_definition vdef where vcourse.pk = vdef.fk_course)
		as shots,
	coalesce(vcourse.comment, '') as comment,
	(select vdef.min_age_due from clin.vaccination_definition vdef where vcourse.pk = vdef.fk_course and vdef.seq_no=1)
		as min_age_due,
	vcourse.is_active as is_active,
	vcourse.fk_indication as pk_indication,
	vcourse.fk_recommended_by as pk_recommended_by,
	vcourse.xmin as xmin_vaccination_course
from
	clin.vaccination_course vcourse,
	clin.vacc_indication vind
where
	vcourse.fk_indication = vind.id
;

comment on view clin.v_vaccination_courses is
	'all vaccination courses known to the system';

-- -----------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_vaccination_definitions4course cascade;
\set ON_ERROR_STOP 1

create view clin.v_vaccination_definitions4course as
select
	vcourse.pk as pk_course,
	vind.description as indication,
	_(vind.description) as l10n_indication,
	coalesce(vcourse.comment, '') as course_comment,
	vcourse.is_active as is_active,
	vdef.id as pk_vaccination_definition,
	vdef.is_booster as is_booster,
	vdef.seq_no as vacc_seq_no,
	vdef.min_age_due as age_due_min,
	vdef.max_age_due as age_due_max,
	vdef.min_interval as min_interval,
	coalesce(vdef.comment, '') as vacc_comment,
	vind.id as pk_indication,
	vcourse.fk_recommended_by as pk_recommended_by
from
	clin.vaccination_course vcourse,
	clin.vacc_indication vind,
	clin.vaccination_definition vdef
where
	vcourse.pk = vdef.fk_course
		and
	vcourse.fk_indication = vind.id
order by
	indication,
	vacc_seq_no
;

comment on view clin.v_vaccination_definitions4course is
	'vaccination event definitions for all courses known to the system';


-- -----------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_vaccination_courses_in_schedule;
\set ON_ERROR_STOP 1

create view clin.v_vaccination_courses_in_schedule as
select
	cvs.name as vaccination_schedule,
	cvc.is_active as is_active,
	cvc.fk_recommended_by as pk_recommended_by,
	cvc.comment as comment_course,
	cvs.comment as comment_schedule,
	cvc.pk as pk_vaccination_course,
	cvc.fk_indication as pk_indication,
	cvs.pk as pk_vaccination_schedule
from
	clin.vaccination_course cvc,
	clin.vaccination_schedule cvs,
	clin.lnk_vaccination_course2schedule clvc2s
where
	clvc2s.fk_course = cvc.pk
		and
	clvc2s.fk_schedule = cvs.pk
;

-- -----------------------------------------------------
create view clin.v_vacc_courses4pat as
select
	lp2vc.fk_patient as pk_patient,
	vvr.indication as indication,
	vvr.l10n_indication as l10n_indication,
	vvr.comment as comment,
	vvr.is_active as is_active,
	vvr.pk_course as pk_course,
	vvr.pk_indication as pk_indication,
	vvr.pk_recommended_by as pk_recommended_by
from
	clin.lnk_pat2vaccination_course lp2vc,
	clin.v_vaccination_courses vvr
where
	vvr.pk_course = lp2vc.fk_course
;

comment on view clin.v_vacc_courses4pat is
	'lists the vaccination courses a patient is actually on';

-- -----------------------------------------------------
create view clin.v_vaccs_scheduled4pat as
select
	vvr4p.pk_patient as pk_patient,
	vvr4p.indication as indication,
	vvr4p.l10n_indication as l10n_indication,
--	vvr4p.course as course,
	vvr4p.comment as course_comment,
	vvd4r.is_booster,
	vvd4r.vacc_seq_no,
	vvd4r.age_due_min,
	vvd4r.age_due_max,
	vvd4r.min_interval,
	vvd4r.vacc_comment as vacc_comment,
	vvd4r.pk_vaccination_definition as pk_vaccination_definition,
	vvr4p.pk_course as pk_course,
	vvr4p.pk_indication as pk_indication,
	vvr4p.pk_recommended_by as pk_recommended_by
from
	clin.v_vacc_courses4pat vvr4p,
	clin.v_vaccination_definitions4course vvd4r
where
	vvd4r.pk_course = vvr4p.pk_course
;

comment on view clin.v_vaccs_scheduled4pat is
	'vaccinations scheduled for a patient according
	 to the vaccination courses he/she is on';

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
	clin.v_inds4vaccine vi4v,
	clin.v_pat_episodes vpep
where
	vpep.pk_episode=v.fk_episode
		and
	v.fk_vaccine = vi4v.pk_vaccine
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
--	vvs4p.course,
	vvs4p.course_comment,
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
	vvs4p.pk_course,
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
	 to the courses a patient is on and the previously
	 received vaccinations';

-- -----------------------------------------------------
-- FIXME: only list those that DO HAVE a previous vacc (max(date) is not null)
create view clin.v_pat_missing_boosters as
select
	vvs4p.pk_patient,
	vvs4p.indication,
	vvs4p.l10n_indication,
--	vvs4p.course,
	vvs4p.course_comment,
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
	vvs4p.pk_course,
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
	 to the courses a patient is on and the previously
	 received vaccinations';

-- -----------------------------------------------------
\unset ON_ERROR_STOP
drop trigger tr_unique_indication_in_schedule on clin.lnk_vaccination_course2schedule;
\set ON_ERROR_STOP 1

create or replace function clin.trf_unique_indication_in_schedule()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_msg text;
BEGIN
	-- is the indication already linked ?
	perform 1 from clin.v_vaccination_courses_in_schedule where
		pk_vaccination_schedule = NEW.fk_schedule and
		pk_indication = (select fk_indication from clin.vaccination_course where pk=NEW.fk_course);
	if FOUND then
		_msg := ''Cannot link course ['' || NEW.fk_course || ''] into schedule ['' || NEW.fk_schedule || '']. The indication is already linked.'';
		raise exception ''%'', _msg;
		return null;
	end if;
	return null;
END;';

create trigger tr_unique_indication_in_schedule
	before insert or update on clin.lnk_vaccination_course2schedule
	for each row execute procedure clin.trf_unique_indication_in_schedule();


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
	, clin.vaccination_definition
	, clin.vaccination_definition_id_seq
	, clin.vaccination_course
	, clin.vaccination_course_pk_seq
	, clin.lnk_pat2vaccination_course
	, clin.lnk_pat2vaccination_course_pk_seq
	, clin.vaccination_course_constraint
	, clin.vaccination_course_constraint_pk_seq
	, clin.lnk_constraint2vacc_course
	, clin.lnk_constraint2vacc_course_pk_seq
	, clin.vaccination_schedule
	, clin.vaccination_schedule_pk_seq
	, clin.lnk_vaccination_course2schedule
	, clin.lnk_vaccination_course2schedule_pk_seq
TO GROUP "gm-doctors";

grant select on
	clin.v_vaccination_courses
	, clin.v_vaccination_definitions4course
	, clin.v_vaccination_courses_in_schedule
	, clin.v_vacc_courses4pat
	, clin.v_vaccs_scheduled4pat
	, clin.v_inds4vaccine
	, clin.v_pat_vacc4ind
	, clin.v_pat_missing_vaccs
	, clin.v_pat_missing_boosters
	, clin.v_vaccine
to group "gm-doctors";

-- ===================================================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmClin-Vaccination-dynamic.sql,v $', '$Revision: 1.6 $');

-- ===================================================================
-- $Log: gmClin-Vaccination-dynamic.sql,v $
-- Revision 1.6  2006-03-07 21:14:10  ncq
-- - fixed trf_unique_indication_in_schedule()
--
-- Revision 1.5  2006/03/06 09:42:46  ncq
-- - spell out more table names
-- - general cleanup
--
-- Revision 1.4  2006/03/04 16:16:27  ncq
-- - adjust to regime -> course name change
-- - enhanced comments
-- - audit more tables
-- - add v_vaccination_courses_in_schedule
-- - adjust grants
--
-- Revision 1.3  2006/02/27 11:24:38  ncq
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
