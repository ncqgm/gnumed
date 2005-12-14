-- Project: GNUmed
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/update_db-v1_v2.sql,v $
-- $Revision: 1.18 $
-- license: GPL
-- author: Ian Haywood, Horst Herb, Karsten Hilbert

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- TODO:
-- - remove scoring stuff
-- - add gmNotifications stuff

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

alter table audited_tables drop constraint audited_tables_table_name_key cascade;
alter table audited_tables add constraint unique_qualified_table unique(schema, table_name);

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
	'{"gmManual","gmNotebookedPatientEditionPlugin","gmEMRBrowserPlugin","gmNotebookedProgressNoteInputPlugin","gmEMRJournalPlugin","gmShowMedDocs","gmScanIdxMedDocsPlugin","gmConfigRegistry"}'
);

-- show document ID after import
insert into cfg.cfg_template
	(name, type, description)
values (
	'horstspace.scan_index.show_doc_id',
	'numeric',
	'1/0, meaning true/false,
	 True: after importing a new document display the document ID,
	 False: do not display the document ID for a new document after import'
);

insert into cfg.cfg_item
	(fk_template, owner)
values (
	currval('cfg.cfg_template_pk_seq'),
	'xxxDEFAULTxxx'
);

-- default to True
insert into cfg.cfg_numeric
	(fk_item, value)
values (
	currval('cfg.cfg_item_pk_seq'),
	1
);

-- remove old options
delete from cfg.cfg_item where workplace='KnoppixMedica';

-- == service clinical ====================================
-- modify source tables

-- * clin_encounter --
alter table public.clin_encounter
	drop column fk_provider cascade;

-- add RFE
alter table public.clin_encounter
	add column rfe text;

-- 1) concat clin_narrative.is_rfe rows into encounter.rfe
create or replace function concat_rfes(integer) returns text as '
declare
	_fk_encounter alias for $1;
	_final_str text;
	_rfe_row record;
begin
	_final_str := ''xxxDEFAULTxxx: '';
	for _rfe_row in select narrative from public.clin_narrative where is_rfe is true and fk_encounter=_fk_encounter loop
		_final_str := _final_str || coalesce(_rfe_row.narrative, '''');
	end loop;
	return _final_str;
end;
' language 'plpgsql';

update public.clin_encounter set
	rfe = (select concat_rfes(public.clin_encounter.id));

drop function concat_rfes(integer);

-- 2) use Soap rows from clin_narrative on remaining ones
create or replace function concat_s(integer) returns text as '
declare
	_fk_encounter alias for $1;
	_final_str text;
	_s_row record;
begin
	_final_str := ''xxxDEFAULTxxx: '';
	for _s_row in select narrative from public.clin_narrative where soap_cat=''s'' and fk_encounter=_fk_encounter loop
		_final_str := _final_str || coalesce(_s_row.narrative, '''');
	end loop;
	return _final_str;
end;
' language 'plpgsql';

update public.clin_encounter set
	rfe = (select concat_s(public.clin_encounter.id))
	where rfe is null;

drop function concat_s(integer);

-- 3) or else just set a default
update clin_encounter set
	rfe = 'xxxDEFAULTxxx'
	where rfe is null;

-- add AOE
alter table public.clin_encounter
	rename column description to aoe;

-- move clin_narrative.is_aoe rows into it
create or replace function concat_aoes(integer) returns text as '
declare
	_fk_encounter alias for $1;
	_final_str text;
	_aoe_row record;
begin
	_final_str = '''';
	for _aoe_row in select narrative from public.clin_narrative where is_aoe is true and fk_encounter=_fk_encounter loop
		_final_str := _final_str || coalesce(_aoe_row.narrative, '''');
	end loop;
	return _final_str;
end;
' language 'plpgsql';

update public.clin_encounter set
	aoe = coalesce(public.clin_encounter.aoe, 'xxxDEFAULTxxx') || ': ' || (select concat_aoes(public.clin_encounter.id));

drop function concat_aoes(integer);

-- * clin_narrative --
delete from public.clin_narrative
	where
		(public.clin_narrative.is_rfe or public.clin_narrative.is_aoe)
		and not exists (select 1 from public.clin_diag cd where cd.fk_narrative = public.clin_narrative.pk)
		and not exists (select 1 from public.hx_family_item hxf where hxf.fk_narrative_condition = public.clin_narrative.pk)
;

alter table public.clin_narrative
	drop constraint aoe_xor_rfe;
alter table public.clin_narrative
	drop constraint rfe_is_subj;
alter table public.clin_narrative
	drop constraint aoe_is_assess;
alter table public.clin_narrative
	drop column is_rfe cascade;
alter table public.clin_narrative
	drop column is_aoe cascade;

-- recreate clinical tables in schema "clin"
\i gmclinical.sql

-- move data and adjust sequences
insert into clin.xlnk_identity select * from public.xlnk_identity;
select setval('clin.xlnk_identity_pk_seq'::text, (select max(pk) from clin.xlnk_identity));

insert into clin.health_issue select * from public.clin_health_issue;
select setval('clin.health_issue_pk_seq'::text, (select max(pk) from clin.health_issue));

insert into clin.episode select * from public.clin_episode;
select setval('clin.episode_pk_seq'::text, (select max(pk) from clin.episode));

insert into clin.encounter_type select * from public.encounter_type;
select setval('clin.encounter_type_pk_seq'::text, (select max(pk) from clin.encounter_type));

insert into clin.encounter
	select
		pk_audit,
		row_version,
		modified_when,
		modified_by,
		id,
		fk_patient,
		fk_type,
		fk_location,
		source_time_zone,
		rfe,
		aoe,
		started,
		last_affirmed
	from public.clin_encounter;
select setval('clin.encounter_id_seq'::text, (select max(id) from clin.encounter));

-- clin_root_item does not need to be moved ...

insert into clin.clin_item_type select * from public.clin_item_type;
select setval('clin.clin_item_type_pk_seq'::text, (select max(pk) from clin.clin_item_type));

insert into clin.lnk_type2item select * from public.lnk_type2item;
select setval('clin.lnk_type2item_pk_seq'::text, (select max(pk) from clin.lnk_type2item));

insert into clin.soap_cat_ranks select * from public.soap_cat_ranks;
select setval('clin.soap_cat_ranks_pk_seq'::text, (select max(pk) from clin.soap_cat_ranks));

insert into clin.clin_narrative select * from public.clin_narrative;
select setval('clin.clin_narrative_pk_seq'::text, (select max(pk) from clin.clin_narrative));

insert into clin.coded_narrative select * from public.coded_narrative;
select setval('clin.coded_narrative_pk_seq'::text, (select max(pk) from clin.coded_narrative));

insert into clin.hx_family_item select * from public.hx_family_item;
select setval('clin.hx_family_item_pk_seq'::text, (select max(pk) from clin.hx_family_item));

insert into clin.clin_hx_family select * from public.clin_hx_family;
select setval('clin.clin_hx_family_pk_seq'::text, (select max(pk) from clin.clin_hx_family));

insert into clin.clin_diag select * from public.clin_diag;
select setval('clin.clin_diag_pk_seq'::text, (select max(pk) from clin.clin_diag));

insert into clin.clin_aux_note select * from public.clin_aux_note;
select setval('clin.clin_aux_note_pk_seq'::text, (select max(pk) from clin.clin_aux_note));

insert into clin.vacc_indication select * from public.vacc_indication;
select setval('clin.vacc_indication_id_seq'::text, (select max(id) from clin.vacc_indication));

insert into clin.lnk_vacc_ind2code select * from public.lnk_vacc_ind2code;
select setval('clin.lnk_vacc_ind2code_id_seq'::text, (select max(id) from clin.lnk_vacc_ind2code));

insert into clin.vacc_route select * from public.vacc_route;
select setval('clin.vacc_route_id_seq'::text, (select max(id) from clin.vacc_route));

insert into clin.vaccine select * from public.vaccine;
select setval('clin.vaccine_id_seq'::text, (select max(id) from clin.vaccine));

insert into clin.lnk_vaccine2inds select * from public.lnk_vaccine2inds;
select setval('clin.lnk_vaccine2inds_id_seq'::text, (select max(id) from clin.lnk_vaccine2inds));

insert into clin.vacc_regime select * from public.vacc_regime;
select setval('clin.vacc_regime_id_seq'::text, (select max(id) from clin.vacc_regime));

insert into clin.lnk_pat2vacc_reg select * from public.lnk_pat2vacc_reg;
select setval('clin.lnk_pat2vacc_reg_pk_seq'::text, (select max(pk) from clin.lnk_pat2vacc_reg));

insert into clin.vacc_def select * from public.vacc_def;
select setval('clin.vacc_def_id_seq'::text, (select max(id) from clin.vacc_def));

insert into clin.vaccination select * from public.vaccination;
select setval('clin.vaccination_id_seq'::text, (select max(id) from clin.vaccination));

insert into clin.allergy_state select * from public.allergy_state;
select setval('clin.allergy_state_id_seq'::text, (select max(id) from clin.allergy_state));

insert into clin._enum_allergy_type select * from public._enum_allergy_type;
select setval('clin._enum_allergy_type_id_seq'::text, (select max(id) from clin._enum_allergy_type));

insert into clin.allergy select * from public.allergy;
select setval('clin.allergy_id_seq'::text, (select max(id) from clin.allergy));

insert into clin.form_instances select * from public.form_instances;
select setval('clin.form_instances_pk_seq'::text, (select max(pk) from clin.form_instances));

insert into clin.form_data select * from public.form_data;
select setval('clin.form_data_pk_seq'::text, (select max(pk) from clin.form_data));

insert into clin.clin_medication select * from public.clin_medication;
select setval('clin.clin_medication_pk_seq'::text, (select max(pk) from clin.clin_medication));

-- drop old tables
drop table public.clin_health_issue cascade;
drop table public.clin_episode cascade;
drop table public.last_act_episode cascade;
drop table public.encounter_type cascade;
drop table public.clin_encounter cascade;
drop table public.curr_encounter cascade;
drop table public.clin_item_type cascade;
drop table public.lnk_type2item cascade;
drop table public.soap_cat_ranks cascade;
drop table public.coded_narrative cascade;
drop table public.hx_family_item cascade;
drop table public.clin_diag cascade;
drop table public.vacc_indication cascade;
drop table public.lnk_vacc_ind2code cascade;
drop table public.vacc_route cascade;
drop table public.vaccine cascade;
drop table public.lnk_vaccine2inds cascade;
drop table public.vacc_regime cascade;
drop table public.lnk_pat2vacc_reg cascade;
drop table public.vacc_def cascade;
drop table public.allergy_state cascade;
drop table public._enum_allergy_type cascade;
drop table public.form_data cascade;
drop table public.enum_confidentiality_level cascade;
drop table public.constituent cascade;

-- * clin_episode, again

-- merge multiple open episodes per issue into one ...

-- select them
create view v_linked_multiple_open_epis as
select *
from clin.clin_episode ce1
where
	is_open and
	(select
		count(*)
	from
		clin.clin_episode ce2
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
	insert into clin.clin_episode (
		fk_health_issue, fk_patient, description, is_open
	) values (
		_fk_health_issue, Null, _new_epi_name, true
	);
	select into _dummy currval(''clin.clin_episode_pk_seq'');
	raise notice ''new episode pk: [%]'', _dummy;
	-- point items to new episode
	raise notice ''now updating clin_root_items'';
	update clin.clin_root_item
		set fk_episode = currval(''clin.clin_episode_pk_seq'')
		where fk_episode in (
			select pk
			from v_linked_multiple_open_epis
			where fk_health_issue = _fk_health_issue
		);
	-- delete all but the new episode
	raise notice ''now deleting old episodes'';
	delete from clin.clin_episode where
		is_open and
		fk_health_issue = _fk_health_issue and
		pk != currval(''clin.clin_episode_pk_seq'');
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

-- recreate measurements tables in schema "clin"
\i gmMeasurements.sql

-- move data and adjust sequences
insert into clin.test_org select * from public.test_org;
select setval('clin.test_org_pk_seq'::text, (select max(pk) from clin.test_org));

insert into clin.test_type select * from public.test_type;
select setval('clin.test_type_pk_seq'::text, (select max(pk) from clin.test_type));

insert into clin.test_type_unified select * from public.test_type_unified;
select setval('clin.test_type_unified_pk_seq'::text, (select max(pk) from clin.test_type_unified));

insert into clin.lnk_ttype2unified_type select * from public.lnk_ttype2unified_type;
select setval('clin.lnk_ttype2unified_type_pk_seq'::text, (select max(pk) from clin.lnk_ttype2unified_type));

insert into clin.lnk_tst2norm select * from public.lnk_tst2norm;
select setval('clin.lnk_tst2norm_id_seq'::text, (select max(id) from clin.lnk_tst2norm));

-- FIXME:
--	fk_intended_reviewer integer
--		not null
--		references clin.xlnk_identity(xfk_identity)
insert into clin.test_result
select
	pk_audit,
	row_version,
	modified_when,
	modified_by,
	pk_item,
	clin_when,
	fk_encounter,
	fk_episode,
	narrative,
	soap_cat,
	pk,
	fk_type,
	val_num,
	val_alpha,
	val_unit,
	val_normal_min,
	val_normal_max,
	val_normal_range,
	val_target_min,
	val_target_max,
	val_target_range,
	technically_abnormal,
	norm_ref_group,
	note_provider,
	material,
	material_detail
from public.test_result;
select setval('clin.test_result_pk_seq'::text, (select max(pk) from clin.test_result));

insert into clin.lab_request select * from public.lab_request;
select setval('clin.lab_request_pk_seq'::text, (select max(pk) from clin.lab_request));

insert into clin.lnk_result2lab_req select * from public.lnk_result2lab_req;
select setval('clin.lnk_result2lab_req_pk_seq'::text, (select max(pk) from clin.lnk_result2lab_req));

-- drop old tables
drop table public.test_org cascade;
drop table public.test_type cascade;
drop table public.test_type_unified cascade;
drop table public.lnk_ttype2unified_type cascade;
drop table public.lnk_tst2norm cascade;
drop table public.lab_request cascade;
drop table public.lnk_result2lab_req cascade;

-- test_result_unmatched --
\i gmUnmatchableData-static.sql
\i gmUnmatchedData-static.sql

insert into clin.incoming_data_unmatched (
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
from public.test_result_unmatched;

select setval('clin.incoming_data_unmatched_pk_seq'::text, (select max(pk) from clin.incoming_data_unmatched));

drop table public.test_result_unmatched cascade;
-- == service blobs ==================================================
-- 1) create tables in schema "blobs"
\i gmBlobs.sql

-- move data from public schema
insert into blobs.xlnk_identity select * from public.xlnk_identity;
insert into blobs.doc_type select * from public.doc_type;
insert into blobs.doc_med select * from public.doc_med;
insert into blobs.doc_obj select * from public.doc_obj;
-- FIXME
--	fk_intended_reviewer integer
--		not null
--		references clin.xlnk_identity(xfk_identity)
insert into blobs.doc_desc select * from public.doc_desc;

-- adjust sequences
select setval('blobs.xlnk_identity_pk_seq'::text, (select max(pk) from blobs.xlnk_identity));
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

-- == service clinical, again ========================================
-- this needs to come after clinical *and* blobs

\i gmReviewedStatus-static.sql

insert into clin.reviewed_test_results (
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
	public.test_result tr
where
	tr.reviewed_by_clinician is true
;

-- drops all child tables, too
drop table public.clin_root_item cascade;

-- adjust clin_root_item sequence globally
select setval('clin.clin_root_item_pk_item_seq'::text, (select max(pk_item) from clin.clin_root_item));

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

-- == cleanup debris =================================================
-- German specific stuff
alter table de_kvk
	rename column straße to strasse;

-- ===================================================================
-- need to do this last
drop table public.xlnk_identity cascade;

-- adjust audit_fields pk sequence globally
select setval('public.audit_fields_pk_audit_seq'::text, (select max(pk_audit) from public.audit_fields));

-- ===================================================================
\unset ON_ERROR_STOP

-- do simple schema revision tracking
select log_script_insertion('$RCSfile: update_db-v1_v2.sql,v $', '$Revision: 1.18 $');

-- =============================================
-- $Log: update_db-v1_v2.sql,v $
-- Revision 1.18  2005-12-14 11:42:21  ncq
-- - we don't have cfg_boolean but rather use cfg_numeric
--
-- Revision 1.17  2005/12/14 10:43:33  ncq
-- - add option on showing document ID after import
-- - several clin.clin_* -> clin.* renames
--
-- Revision 1.16  2005/11/29 19:09:59  ncq
-- - properly modified audited_tables
-- - add scanidxpnl to Librarian release config
-- - re-arrange clinical upgrade
--
-- Revision 1.15  2005/11/25 15:05:13  ncq
-- - start upgrading things to "clin" schema - not functional yet
--
-- Revision 1.14  2005/11/19 13:51:14  ncq
-- - rename latin1 column straße to strasse
--
-- Revision 1.13  2005/11/18 15:56:55  ncq
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
