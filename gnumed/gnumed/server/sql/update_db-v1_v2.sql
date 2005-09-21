-- Project: GNUmed
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/update_db-v1_v2.sql,v $
-- $Revision: 1.3 $
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

-- -- RFE ----------------------------------------------
-- add clin_encounter.rfe
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

-- now forbid nulls
alter table clin_encounter
	alter column rfe
		set not null;

-- drop rfe constraints
alter table clin_narrative
	drop constraint aoe_xor_rfe;
alter table clin_narrative
	drop constraint rfe_is_subj;

-- -- AOE ----------------------------------------------
alter table clin_encounter
	rename column description to aoe;

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

-- disallow nulls
alter table clin_encounter
	alter column aoe
		set not null;

-- drop aoe constraints
alter table clin_narrative
	drop constraint aoe_is_assess;

-- drop old data ---------------------------------------
-- delete is_rfe/is_aoe=true rows from clin_narrative
delete from clin_narrative
	where
		(clin_narrative.is_rfe or clin_narrative.is_aoe)
		and not exists (select 1 from clin_diag cd where cd.fk_narrative = clin_narrative.pk)
		and not exists (select 1 from hx_family_item hxf where hxf.fk_narrative_condition = clin_narrative.pk)
;

-- drop columns ----------------------------------------
-- is_rfe from clin_narrative ...
alter table clin_narrative
	drop column is_rfe cascade;

-- is_aoe from clin_narrative ...
alter table clin_narrative
	drop column is_aoe cascade;

-- curr_encounter --------------------------------------
drop table curr_encounter;

-- gm_schema_revision ----------------------------------
alter table gm_schema_revision
	drop column is_core cascade;

-- ===================================================================
\i gmWaitingList.sql

-- ===================================================================
\unset ON_ERROR_STOP

-- do simple schema revision tracking
delete from gm_schema_revision where filename='$RCSfile: update_db-v1_v2.sql,v $';
insert into gm_schema_revision (filename, version) values('$RCSfile: update_db-v1_v2.sql,v $', '$Revision: 1.3 $');

-- =============================================
-- $Log: update_db-v1_v2.sql,v $
-- Revision 1.3  2005-09-21 10:22:34  ncq
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
