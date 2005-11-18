-- Project: GNUmed
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/update_db-v1_v2.sql,v $
-- $Revision: 1.13 $
-- license: GPL
-- author: Ian Haywood, Horst Herb, Karsten Hilbert

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- == cross-service =======================================

-- gm_schema_revision --
alter table gm_schema_revision
	drop column is_core cascade;

-- audited_tables.schema --
alter table audited_tables
	alter column "schema"
		set default 'public';

update audited_tables set "schema" = DEFAULT where "schema" is null;

alter table audited_tables
	alter column "schema"
		set not null;

-- == service default =====================================
-- create tables in new schema cfg.
\i gmConfig-static.sql

-- move over data
insert into cfg.db select * from public.db;
insert into cfg.distributed_db select * from public.distributed_db;
insert into cfg.config select * from public.config;
insert into cfg.cfg_type_enum select * from public.cfg_type_enum;
insert into cfg.cfg_template select * from public.cfg_template;
insert into cfg.cfg_item select * from public.cfg_item;
insert into cfg.cfg_string select * from public.cfg_string;
insert into cfg.cfg_numeric select * from public.cfg_numeric;
insert into cfg.cfg_str_array select * from public.cfg_str_array;
insert into cfg.cfg_data select * from public.cfg_data;

-- adjust sequences since we copied over the primary keys, too
select setval('cfg.db_id_seq'::text, (select max(id) from cfg.db));
select setval('cfg.distributed_db_id_seq'::text, (select max(id) from cfg.distributed_db));
select setval('cfg.config_id_seq'::text, (select max(id) from cfg.config));
select setval('cfg.cfg_template_pk_seq'::text, (select max(pk) from cfg.cfg_template));
select setval('cfg.cfg_item_pk_seq'::text, (select max(pk) from cfg.cfg_item));

-- drop old tables
drop table public.db cascade;
drop table public.distributed_db cascade;
drop table public.config cascade;
drop table public.cfg_type_enum cascade;
drop table public.cfg_template cascade;
drop table public.cfg_item cascade;
drop table public.cfg_string cascade;
drop table public.cfg_numeric cascade;
drop table public.cfg_str_array cascade;
drop table public.cfg_data cascade;

-- add new options
\unset ON_ERROR_STOP
insert into cfg.cfg_template
	(name, type, description)
values (
	'patient_search.always_reload_new_patient',
	'numeric',
	'1/0, meaning true/false,
	 if true: reload patient data after search even if the new patient is the same as the previous one,
	 if false: do not reload data if new patient matches previous one'
);

insert into cfg.cfg_item
	(fk_template, owner, workplace)
values (
	currval('cfg.cfg_template_pk_seq'),
	'xxxDEFAULTxxx',
	'xxxDEFAULTxxx'
);

-- default to false
insert into cfg.cfg_numeric
	(fk_item, value)
values (
	currval('cfg.cfg_item_pk_seq'),
	0
);
\set ON_ERROR_STOP 1

-- a 'workplace' called "Librarian (0.2)" --
insert into cfg.cfg_item
	(fk_template, owner, workplace)
values (
	(select pk from cfg.cfg_template where name='horstspace.notebook.plugin_load_order'),
	'xxxDEFAULTxxx',
	'Librarian Release (0.2)'
);

insert into cfg.cfg_str_array
	(fk_item, value)
values (
	currval('cfg.cfg_item_pk_seq'),
	'{"gmManual","gmNotebookedPatientEditionPlugin","gmEMRBrowserPlugin","gmNotebookedProgressNoteInputPlugin","gmEMRJournalPlugin","gmShowMedDocs","gmConfigRegistry"}'
);

-- remove old data
delete from cfg.cfg_item where workplace='KnoppixMedica';

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

-- curr_encounter --
drop table curr_encounter;

-- last_act_episode --
drop table last_act_episode;

-- == service blobs ==================================================
-- 1) create tables in schema "blobs"
\i gmBlobs.sql

-- move data from public schema
insert into blobs.doc_type select * from public.doc_type;
insert into blobs.doc_med select * from public.doc_med;
insert into blobs.doc_obj select * from public.doc_obj;
insert into blobs.doc_desc select * from public.doc_desc;

-- adjust sequences
select setval('blobs.doc_type_pk_seq'::text, (select max(pk) from blobs.doc_type));
select setval('blobs.doc_med_id_seq'::text, (select max(id) from blobs.doc_med));
select setval('blobs.doc_obj_id_seq'::text, (select max(id) from blobs.doc_obj));
select setval('blobs.doc_desc_id_seq'::text, (select max(id) from blobs.doc_desc));

-- drop tables in public schema
drop table public.doc_desc cascade;
drop table public.doc_obj cascade;
drop table public.doc_med cascade;
drop table public.doc_type cascade;

-- doc_type --
-- set all doc_types to system
update blobs.doc_type
	set is_user = false;

-- ===================================================================
-- review tables/views --
\i gmReviewedStatus-static.sql

-- test_result --
alter table test_result
	drop column fk_doc cascade;

insert into reviewed_test_results (
	fk_reviewed_row,
	fk_reviewer,
	is_technically_abnormal,
	clinically_relevant
) select
	tr.pk,
	tr.fk_reviewer,
	case when tr.technically_abnormal is null
		then false
		else true
	end as is_abnormal,
	tr.clinically_relevant
from
	test_result tr
where
	tr.reviewed_by_clinician is true
;

alter table test_result
	drop column clinically_relevant cascade;
alter table test_result
	drop column fk_reviewer cascade;
alter table test_result
	drop column reviewed_by_clinician cascade;

alter table test_result
	rename column technically_abnormal to abnormality_indicator;

-- test_result_unmatched --
\i gmUnmatchableData-static.sql
\i gmUnmatchedData-static.sql

insert into incoming_data_unmatched (
	pk,
	fk_patient_candidates,
	request_id,
	firstnames,
	lastnames,
	dob,
	postcode,
	other_info,
	type,
	data
) select
	pk,
	fk_patient_candidates,
	request_id,
	firstnames,
	lastnames,
	dob,
	postcode,
	other_info,
	type,
	decode(data, 'escape')			-- textsend()
from test_result_unmatched;

drop table test_result_unmatched cascade;

-- == service reference ==============================================

-- form_defs
alter table form_defs
	add column is_user boolean;
update form_defs
	set is_user = false;
alter table form_defs
	alter column is_user
		set not null;
alter table form_defs
	alter column is_user
		set default true;

-- == cleanup debris =================================================
\unset ON_ERROR_STOP
drop function calc_db_identity_hash();
drop function log_script_insertion(text, text, boolean);
\set ON_ERROR_STOP 1

-- ===================================================================
\unset ON_ERROR_STOP

-- do simple schema revision tracking
select log_script_insertion('$RCSfile: update_db-v1_v2.sql,v $', '$Revision: 1.13 $');

-- =============================================
-- $Log: update_db-v1_v2.sql,v $
-- Revision 1.13  2005-11-18 15:56:55  ncq
-- - gmconfiguration.sql -> gmConfig-static.sql
--
-- Revision 1.12  2005/11/18 15:44:32  ncq
-- - move configuration objects to new cfg.* schema
-- - need to setval() sequences after moving data from public into blobs/cfg
--   schemata since we "insert ... select ..." all columns including pk
--
-- Revision 1.11  2005/11/11 23:06:48  ncq
-- - add is_user to doc_type and form_defs
--
-- Revision 1.10  2005/11/01 08:55:49  ncq
-- - add 0.2 workplace plugin config
-- - rename test_result_unmatched to incoming_data_unmatched and move data
--
-- Revision 1.9  2005/10/26 21:31:09  ncq
-- - review status tracking
--
-- Revision 1.8  2005/10/24 19:30:23  ncq
-- - require schema in audited_tables - default to public
-- - move blobs service into schema "blobs"
--
-- Revision 1.7  2005/10/12 19:24:25  ncq
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
