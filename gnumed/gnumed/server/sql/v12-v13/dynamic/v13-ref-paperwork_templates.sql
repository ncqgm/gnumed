-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
alter table ref.paperwork_templates drop constraint paperwork_templates_engine_check cascade;
\set ON_ERROR_STOP 1


alter table ref.paperwork_templates
	add constraint engine_range
		check (engine in ('T', 'L', 'H', 'O', 'I'));


comment on column ref.paperwork_templates.engine is
'the business layer forms engine used to process this form, currently:
	- T: plain text
	- L: LaTeX
	- H: Health Layer 7
	- O: OpenOffice
	- I: image editor (visual progress notes)'
;

-- --------------------------------------------------------------
-- visual progress note template type
\unset ON_ERROR_STOP
insert into ref.form_types (name) values (i18n.i18n('visual progress note'));
\set ON_ERROR_STOP 1

select i18n.upd_tx('de_DE', 'visual progress note', 'Bildnotiz');

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-ref-paperwork_templates.sql,v $', '$Revision: 1.3 $');
