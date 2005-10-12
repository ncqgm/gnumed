-- Project: GNUmed
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/update_db-v1_v2.sql,v $
-- $Revision: 1.7 $
-- license: GPL
-- author: Ian Haywood, Horst Herb, Karsten Hilbert

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- == service default =====================================

\unset ON_ERROR_STOP
-- reload patient data after search even if same patient
insert into cfg_template
	(name, type, description)
values (
	'patient_search.always_reload_new_patient',
	'numeric',
	'1/0, meaning true/false,
	 if true: reload patient data after search even if the new patient is the same as the previous one,
	 if false: do not reload data if new patient matches previous one'
);

insert into cfg_item
	(id_template, owner, workplace)
values (
	currval('cfg_template_id_seq'),
	'xxxDEFAULTxxx',
	'xxxDEFAULTxxx'
);

-- default to false
insert into cfg_numeric
	(id_item, value)
values (
	currval('cfg_item_id_seq'),
	0
);
\set ON_ERROR_STOP 1

-- == service clinical ====================================

-- clin_episode ----------------------------------------

-- merge multiple open episodes per issue into one ...

-- select them
create view v_linked_multiple_open_epis as
select *
from clin_episode ce1
where
	is_open and
	(select
		count(*)
	from
		clin_episode ce2
	where
		is_open and
		ce2.fk_health_issue = ce1.fk_health_issue
	) > 1
;

-- merge functions
create or replace function merge_open_epis(integer)
	returns void
	language 'plpgsql'
as '
declare
	_fk_health_issue alias for $1;
	_new_epi_name text;
	_old_epi_row record;
	_dummy integer;
begin
	raise notice ''merging episodes on health issue %'', _fk_health_issue;
	-- sanity check
	select into _dummy 1 from v_linked_multiple_open_epis where fk_health_issue = _fk_health_issue;
	if not found then
		raise notice ''no episode found'';
		return;
	end if;
	-- aggregate descriptions
	_new_epi_name := '''';
	for _old_epi_row in
		select description from v_linked_multiple_open_epis where fk_health_issue = _fk_health_issue
	loop
		raise notice ''old description [%]'', _old_epi_row.description;
		_new_epi_name := _new_epi_name || _old_epi_row.description || '' // '';
	end loop;
	raise notice ''new description [%]'', _new_epi_name;
	-- create new episode
	insert into clin_episode (
		fk_health_issue, fk_patient, description, is_open
	) values (
		_fk_health_issue, Null, _new_epi_name, true
	);
	select into _dummy currval(''clin_episode_pk_seq'');
	raise notice ''new episode pk: [%]'', _dummy;
	-- point items to new episode
	raise notice ''now updating clin_root_items'';
	update clin_root_item
		set fk_episode = currval(''clin_episode_pk_seq'')
		where fk_episode in (
			select pk
			from v_linked_multiple_open_epis
			where fk_health_issue = _fk_health_issue
		);
	-- delete all but the new episode
	raise notice ''now deleting old episodes'';
	delete from clin_episode where
		is_open and
		fk_health_issue = _fk_health_issue and
		pk != currval(''clin_episode_pk_seq'');
	return;
end;
';

create or replace function do_epi_merge()
	returns void
	language 'plpgsql'
as '
declare
	_epi_row record;
begin
	for _epi_row in select distinct fk_health_issue from v_linked_multiple_open_epis loop
		perform merge_open_epis(_epi_row.fk_health_issue);
	end loop;
	return;
end;
';

-- actually merge them
select do_epi_merge();

-- cleanup
drop function merge_open_epis(integer);
drop function do_epi_merge();
drop view v_linked_multiple_open_epis;

-- -- clin_encounter -----------------------------------

-- -- RFE --
alter table clin_encounter
	add column rfe text;

comment on column clin_encounter.rfe is
	'the RFE for the encounter as related by either
	 the patient or the provider (say, in a chart
	 review)';

-- add content to it:
-- 1) use is_rfe rows from clin_narrative
create or replace function concat_rfes(integer) returns text as '
declare
	_fk_encounter alias for $1;
	_final_str text;
	_rfe_row record;
begin
	_final_str := ''xxxDEFAULTxxx: '';
	for _rfe_row in select narrative from clin_narrative where is_rfe is true and fk_encounter=_fk_encounter loop
		_final_str := _final_str || coalesce(_rfe_row.narrative, '''');
	end loop;
	return _final_str;
end;
' language 'plpgsql';

update clin_encounter set
	rfe = (select concat_rfes(clin_encounter.id));

drop function concat_rfes(integer);

-- 2) use Soap rows from clin_narrative on remaining ones
create or replace function concat_s(integer) returns text as '
declare
	_fk_encounter alias for $1;
	_final_str text;
	_s_row record;
begin
	_final_str := ''xxxDEFAULTxxx: '';
	for _s_row in select narrative from clin_narrative where soap_cat=''s'' and fk_encounter=_fk_encounter loop
		_final_str := _final_str || coalesce(_s_row.narrative, '''');
	end loop;
	return _final_str;
end;
' language 'plpgsql';

update clin_encounter set
	rfe = (select concat_s(clin_encounter.id))
	where rfe is null;

drop function concat_s(integer);

-- 3) or else just set a default
update clin_encounter set
	rfe = 'xxxDEFAULTxxx'
	where rfe is null;

-- -- AOE --
alter table clin_encounter
	rename column description to aoe;

comment on column clin_encounter.aoe is
	'the Assessment of Encounter (eg consultation summary)
	 as determined by the provider, may simply be a
	 concatenation of soAp narrative, this assessment
	 should go across all problems';

-- move clin_narrative.is_aoe rows into it
create or replace function concat_aoes(integer) returns text as '
declare
	_fk_encounter alias for $1;
	_final_str text;
	_aoe_row record;
begin
	_final_str = '''';
	for _aoe_row in select narrative from clin_narrative where is_aoe is true and fk_encounter=_fk_encounter loop
		_final_str := _final_str || coalesce(_aoe_row.narrative, '''');
	end loop;
	return _final_str;
end;
' language 'plpgsql';

update clin_encounter set
	aoe = coalesce(clin_encounter.aoe, 'xxxDEFAULTxxx') || ': ' || (select concat_aoes(clin_encounter.id));

drop function concat_aoes(integer);

-- -- fk_provider --
alter table clin_encounter
	drop column fk_provider cascade;

-- clin_narrative ---------------------------------

-- drop rfe constraints
alter table clin_narrative
	drop constraint aoe_xor_rfe;
alter table clin_narrative
	drop constraint rfe_is_subj;

-- drop aoe constraints
alter table clin_narrative
	drop constraint aoe_is_assess;

-- delete is_rfe/is_aoe=true rows
delete from clin_narrative
	where
		(clin_narrative.is_rfe or clin_narrative.is_aoe)
		and not exists (select 1 from clin_diag cd where cd.fk_narrative = clin_narrative.pk)
		and not exists (select 1 from hx_family_item hxf where hxf.fk_narrative_condition = clin_narrative.pk)
;

-- drop is_rfe ...
alter table clin_narrative
	drop column is_rfe cascade;

-- drop is_aoe ...
alter table clin_narrative
	drop column is_aoe cascade;

-- curr_encounter --------------------------------------
drop table curr_encounter;

-- last_act_episode ------------------------------------
drop table last_act_episode;

-- gm_schema_revision ----------------------------------
alter table gm_schema_revision
	drop column is_core cascade;

-- ===================================================================
-- add tables, data, etc
\i gmWaitingList.sql
\i gmCountryZones.sql

-- ===================================================================
\unset ON_ERROR_STOP

-- do simple schema revision tracking
delete from gm_schema_revision where filename='$RCSfile: update_db-v1_v2.sql,v $';
insert into gm_schema_revision (filename, version) values('$RCSfile: update_db-v1_v2.sql,v $', '$Revision: 1.7 $');

-- =============================================
-- $Log: update_db-v1_v2.sql,v $
-- Revision 1.7  2005-10-12 19:24:25  ncq
-- - clin_encounter.rfe can be null
--
-- Revision 1.6  2005/09/25 17:51:14  ncq
-- - include country zones
-- - drop last_act_episode
-- - if a health issue has several open episodes merge them
--   into one as we don't allow that anymore, don't lose data
--   in the process if we can help it
--
-- Revision 1.5  2005/09/22 15:50:00  ncq
-- - cascade column drop
--
-- Revision 1.4  2005/09/22 15:41:58  ncq
-- - cleanup
-- - sync comments
-- - drop fk_provider
--
-- Revision 1.3  2005/09/21 10:22:34  ncq
-- - selectively delete is_rfe/is_aoe rows in clin_narrative
-- - include waiting list
--
-- Revision 1.2  2005/09/19 16:23:08  ncq
-- - adjust to rfe/aoe changes (clin_encounter)
-- - adjust to dropping is_core
--
-- Revision 1.1  2005/09/13 11:54:47  ncq
-- - initial update of v1 -> v2: config option
--
