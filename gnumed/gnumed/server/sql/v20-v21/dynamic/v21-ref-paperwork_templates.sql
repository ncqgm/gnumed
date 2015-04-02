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
delete from ref.paperwork_templates where name_long = 'Medikationsplan (Deutschland, AMTS)';

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
	'Medikationsplan (Deutschland, AMTS)',
	'DE-DE-Version 2.0 vom 15.12.2014',
	'L',
	'amts-med-plan.tex',
	false,
	'real template missing'::bytea
);

-- --------------------------------------------------------------
delete from ref.paperwork_templates where name_long = 'Medikationsplan (Deutschland, NICHT konform zu AMTS)';

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
	'MedPlan (D, ähnlich AMTS)',
	'Medikationsplan (Deutschland, NICHT konform zu AMTS)',
	'v21.0 (nicht konform zu DE-DE-Version 2.0 vom 15.12.2014)',
	'L',
	'not-amts-med-plan.tex',
	false,
	'real template missing'::bytea
);

-- --------------------------------------------------------------
delete from ref.paperwork_templates where name_long = 'Liste aktueller Medikamente (GNUmed)';

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
	'Med.Liste (GMd)',
	'Liste aktueller Medikamente (GNUmed)',
	'21.0',
	'L',
	'akt-med-liste.tex',
	false,
	'real template missing'::bytea
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-ref-paperwork_templates.sql', '21.0');
