-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
insert into ref.form_types (name) values (i18n.i18n('form header'));
\set ON_ERROR_STOP 1

select i18n.upd_tx('de', 'form header', 'Formularkopf');

delete from ref.paperwork_templates where name_long = 'Formularkopf (GNUmed-Vorgabe)';

insert into ref.paperwork_templates (
	fk_template_type,
	instance_type,
	name_short,
	name_long,
	external_version,
	engine,
	filename,
	data
) values (
	(select pk from ref.form_types where name = 'form header'),
	'other form',
	'Formularkopf (GMd)',
	'Formularkopf (GNUmed-Vorgabe)',
	'v16.0',
	'L',
	'form-header.tex',
	'real template missing'::bytea
);

select i18n.upd_tx('de', 'other form', 'sonstiges Formular');

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-ref-paperwork_templates.sql', 'v16');
