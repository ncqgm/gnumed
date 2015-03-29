-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
delete from ref.paperwork_templates where name_long = 'Medikationsplan (AMTS Deutschland)';

insert into ref.paperwork_templates (
	fk_template_type,
	instance_type,
	name_short,
	name_long,
	external_version,
	engine,
	filename,
	edit_after_substitution,
	data
) values (
	(select pk from ref.form_types where name = 'current medication list'),
	'current medication list',
	'MedPlan AMTS (D)',
	'Medikationsplan (AMTS Deutschland)',
	'DE-DE-Version 2.0 vom 15.12.2014',
	'L',
	'amts-med-plan.tex',
	false,
	'real template missing'::bytea
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-ref-paperwork_templates.sql', '21.0');
