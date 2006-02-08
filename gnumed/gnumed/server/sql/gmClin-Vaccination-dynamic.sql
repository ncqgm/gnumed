-- Project: GNUmed - vaccination related dynamic relations
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmClin-Vaccination-dynamic.sql,v $
-- $Revision: 1.1 $
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
	'maximum age this vaccine is licensed for according to the information by the manufacturer';

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
	 if max_age_due = NULL: no maximum age';
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
to group "gm-doctors";



-- ===================================================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmClin-Vaccination-dynamic.sql,v $', '$Revision: 1.1 $');

-- ===================================================================
-- $Log: gmClin-Vaccination-dynamic.sql,v $
-- Revision 1.1  2006-02-08 15:15:39  ncq
-- - factor our vaccination stuff into its own set of files
-- - remove clin.lnk_vacc_ind2code in favour of clin.coded_term usage
-- - improve comments as discussed on the list
--
--
