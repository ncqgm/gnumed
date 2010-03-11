-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- example form template
\unset ON_ERROR_STOP
insert into ref.form_types (name) values (i18n.i18n('visual progress note'));
\set ON_ERROR_STOP 1

select i18n.upd_tx('de_DE', 'visual progress note', 'Bildnotiz');

--delete from ref.paperwork_templates where name_long = 'Current medication list (GNUmed default)';

--insert into ref.paperwork_templates (
--	fk_template_type,
--	name_short,
--	name_long,
--	external_version,
--	engine,
--	filename,
--	data
--) values (
--	(select pk from ref.form_types where name = 'current medication list'),
--	'Medication list (GNUmed)',
--	'Current medication list (GNUmed default)',
--	'1.0',
--	'L',
--	'medslist.tex',
--	'real template missing'::bytea
--);

-- --------------------------------------------------------------
-- --------------------------------------------------------------
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-ref-paperwork_templates.sql,v $', '$Revision: 1.3 $');
