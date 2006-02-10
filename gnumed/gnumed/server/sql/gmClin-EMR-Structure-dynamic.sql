-- Project: GNUmed - EMR structure related dynamic relations:
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmClin-EMR-Structure-dynamic.sql,v $
-- $Revision: 1.1 $
-- license: GPL
-- author: Ian Haywood, Karsten Hilbert

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
-- -- clin.xlnk_identity --
--select add_x_db_fk_def('clin.xlnk_identity', 'xfk_identity', 'personalia', 'identity', 'pk');
select audit.add_table_for_audit('clin', 'xlnk_identity');

comment on table clin.xlnk_identity is
	'this is the one table with the unresolved identity(pk)
	 foreign key, all other tables in this service link to
	 this table, depending upon circumstances one can add
	 dblink() verification or a true FK constraint (if "personalia"
	 is in the same database as "historica")';

-- -- clin.health_issue --
select audit.add_table_for_audit('clin', 'health_issue');

comment on table clin.health_issue is
	'This is pretty much what others would call "Past Medical History"
	 or "Foundational illness", eg. longer-ranging, underlying,
	 encompassing issues with one''s health such as "immunodeficiency",
	 "type 2 diabetes". In Belgium it is called "problem".
	 L.L.Weed includes lots of little things into it, we do not.';
comment on column clin.health_issue.id_patient is
 	'id of patient this health issue relates to, should
	 be reference but might be outside our own database';
comment on column clin.health_issue.description is
	'descriptive name of this health issue, may
	 change over time as evidence increases';
comment on column clin.health_issue.age_noted is
	'at what age the patient acquired the condition';
comment on column clin.health_issue.is_active is
	'whether this health issue (problem) is active';
comment on column clin.health_issue.clinically_relevant is
	'whether this health issue (problem) has any clinical relevance';

alter table clin.health_issue add constraint issue_name_not_empty
	check (trim(both from description) != '');

-- -- clin.episode --
select audit.add_table_for_audit('clin', 'episode');

comment on table clin.episode is
	'Clinical episodes such as "Otitis media",
	 "traffic accident 7/99", "Hepatitis B".
	 This covers a range of time in which
	 activity of illness was noted for the
	 problem episode.description.';
comment on column clin.episode.fk_health_issue is
	'health issue this episode belongs to';
comment on column clin.episode.fk_patient is
	'patient this episode belongs to,
	 may only be set if fk_health_issue is Null
	 thereby removing redundancy';
comment on column clin.episode.description is
	'description/name of this episode';
comment on column clin.episode.is_open is
	'whether the episode is open (eg. there is activity for it),
	 means open in a temporal sense as in "not closed yet";
	 only one episode can be open per health issue';

alter table clin.episode add constraint only_standalone_epi_has_patient
	check (
		((fk_health_issue is null) and (fk_patient is not null))
			or
		((fk_health_issue is not null) and (fk_patient is null))
	);

-- -- clin.encounter_type --
comment on TABLE clin.encounter_type is
	'these are the types of encounter';

-- -- clin.encounter --
--select add_x_db_fk_def('encounter', 'fk_location', 'personalia', 'org', 'id');

comment on table clin.encounter is
	'a clinical encounter between a person and the health care system';
comment on COLUMN clin.encounter.fk_patient is
	'PK of subject of care, should be PUPIC, actually';
comment on COLUMN clin.encounter.fk_type is
	'PK of type of this encounter';
comment on COLUMN clin.encounter.fk_location is
	'PK of location *of care*, e.g. where the provider is at';
comment on column clin.encounter.source_time_zone is
	'time zone of location, used to approximate source time
	 zone for all timestamps in this encounter';
comment on column clin.encounter.rfe is
	'the RFE for the encounter as related by either
	 the patient or the provider (say, in a chart
	 review)';
comment on column clin.encounter.aoe is
	'the Assessment of Encounter (eg consultation summary)
	 as determined by the provider, may simply be a
	 concatenation of soAp narrative, this assessment
	 should go across all problems';

-- ==========================================================
-- health issues stuff
\unset ON_ERROR_STOP
drop function clin.f_announce_h_issue_mod() cascade;
\set ON_ERROR_STOP 1

create function clin.f_announce_h_issue_mod() returns opaque as '
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
	on clin.health_issue
	for each row
		execute procedure clin.f_announce_h_issue_mod()
;

-- =============================================
-- encounters

\unset ON_ERROR_STOP
drop index clin.idx_pat_per_encounter;
drop index clin.idx_encounter_started;
drop index clin.idx_encounter_affirmed;
\set ON_ERROR_STOP 1

create index idx_pat_per_encounter on clin.encounter(fk_patient);
create index idx_encounter_started on clin.encounter(started);
create index idx_encounter_affirmed on clin.encounter(last_affirmed);


\unset ON_ERROR_STOP
drop function f_set_encounter_timezone() cascade;
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
	on clin.encounter
	for each row
		execute procedure f_set_encounter_timezone()
;

-- per patient
\unset ON_ERROR_STOP
drop view clin.v_pat_encounters cascade;
\set ON_ERROR_STOP 1

create view clin.v_pat_encounters as
select
	cle.pk as pk_encounter,
	cle.fk_patient as pk_patient,
	cle.started as started,
	et.description as type,
	_(et.description) as l10n_type,
	cle.rfe as rfe,
	cle.aoe as aoe,
	cle.last_affirmed as last_affirmed,
	cle.fk_location as pk_location,
	cle.fk_type as pk_type,
	cle.xmin as xmin_encounter
from
	clin.encounter cle,
	clin.encounter_type et
where
	cle.fk_type = et.pk
;

-- current ones
\unset ON_ERROR_STOP
drop view clin.v_most_recent_encounters cascade;
\set ON_ERROR_STOP 1

create view clin.v_most_recent_encounters as
select distinct on (last_affirmed)
	ce1.pk as pk_encounter,
	ce1.fk_patient as pk_patient,
	ce1.rfe as rfe,
	ce1.aoe as aoe,
	et.description as type,
	_(et.description) as l10n_type,
	ce1.started as started,
	ce1.last_affirmed as last_affirmed,
	ce1.fk_type as pk_type,
	ce1.fk_location as pk_location
from
	clin.encounter ce1,
	clin.encounter_type et
where
	ce1.fk_type = et.pk
		and
	ce1.started = (
		-- find max of started in ...
		select max(started)
		from clin.encounter ce2
		where
			ce2.last_affirmed = (
				-- ... max of last_affirmed for patient
				select max(last_affirmed)
				from clin.encounter ce3
				where
					ce3.fk_patient = ce1.fk_patient
			)
		limit 1
	)
;

-- =============================================
-- episodes stuff

-- speed up access by fk_health_issue
\unset ON_ERROR_STOP
drop index clin.idx_episode_issue;
drop index clin.idx_episode_valid_issue;
create index idx_episode_valid_issue on clin.episode(fk_health_issue) where fk_health_issue is not null;
\set ON_ERROR_STOP 1
create index idx_episode_issue on clin.episode(fk_health_issue);

\unset ON_ERROR_STOP
drop index clin.idx_uniq_open_epi_per_issue;
\set ON_ERROR_STOP 1
create unique index idx_uniq_open_epi_per_issue on clin.episode(is_open, fk_health_issue) where fk_health_issue is not null and is_open;


\unset ON_ERROR_STOP
drop function trf_announce_episode_mod() cascade;
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
				from clin.health_issue
				where pk = OLD.fk_health_issue;
		else
			patient_id := OLD.fk_patient;
		end if;
	else
		-- if no patient in episode
		if NEW.fk_patient is null then
			-- get it from attached health issue
			select into patient_id id_patient
				from clin.health_issue
				where pk = NEW.fk_health_issue;
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
	on clin.episode
	for each row
		execute procedure trf_announce_episode_mod()
;

\unset ON_ERROR_STOP
drop view clin.v_pat_episodes cascade;
\set ON_ERROR_STOP 1

create view clin.v_pat_episodes as
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
	cep.xmin as xmin_episode
from
	clin.episode cep
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
	cep.xmin as xmin_episode
from
	clin.episode cep, clin.health_issue chi
where
	-- this should exclude all (fk_health_issue is Null) ?
	cep.fk_health_issue=chi.pk
;


-- =============================================
-- schema
grant usage on schema clin to group "gm-doctors";

-- =============================================
-- tables
GRANT SELECT, INSERT, UPDATE, DELETE ON
	clin.health_issue
	, clin.health_issue_pk_seq
	, clin.episode
	, clin.episode_pk_seq
	, clin.encounter_type
	, clin.encounter_type_pk_seq
	, clin.encounter
	, clin.encounter_pk_seq
TO GROUP "gm-doctors";

-- views
grant select on
	clin.v_pat_encounters
	, clin.v_pat_episodes
	, clin.v_most_recent_encounters
TO GROUP "gm-doctors";

-- ===================================================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmClin-EMR-Structure-dynamic.sql,v $', '$Revision: 1.1 $');

-- ===================================================================
-- $Log: gmClin-EMR-Structure-dynamic.sql,v $
-- Revision 1.1  2006-02-10 14:08:58  ncq
-- - factor out EMR structure clinical schema into its own set of files
--
--
