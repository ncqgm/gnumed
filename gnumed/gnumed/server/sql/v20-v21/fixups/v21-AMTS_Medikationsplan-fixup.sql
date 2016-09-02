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
update ref.paperwork_templates set
	name_long = 'Medikationsplan 2.0 (Deutschland, AMTS)',
	name_short = 'MedPlan AMTS (D,2.0)',
	gnumed_revision = '21.7',
	in_use = false
where
	name_long = 'Medikationsplan (Deutschland, AMTS)';

-- --------------------------------------------------------------
delete from ref.paperwork_templates where name_long = 'Medikationsplan 2.3 (AMTS, Deutschland)';

insert into ref.paperwork_templates (
	fk_template_type,
	instance_type,
	name_short,
	name_long,
	external_version,
	gnumed_revision,
	engine,
	filename,
	edit_after_substitution,
	data
) values (
	(select pk from ref.form_types where name = 'current medication list'),
	'current medication list',
	'MedPlan AMTS 2.3 (D)',
	'Medikationsplan 2.3 (AMTS, Deutschland)',
	'de-DE-2.3 AMTS',
	21.8,
	'L',
	'amts-med_plan-2_3.tex',
	false,
	'real template missing'::bytea
);

-- --------------------------------------------------------------
update ref.paperwork_templates set
	name_long = 'Medikationsplan (Deutschland, NICHT konform zu AMTS 2.0)',
	name_short = 'MedPlan AMTS (ähnlich 2.0, D)',
	gnumed_revision = '21.7',
	in_use = false
where
	name_long = 'Medikationsplan (Deutschland, NICHT konform zu AMTS)';


-- --------------------------------------------------------------
delete from ref.paperwork_templates where name_long = 'Medikationsplan AMTS (~2.3, NICHT konform, Deutschland)';

insert into ref.paperwork_templates (
	fk_template_type,
	instance_type,
	name_short,
	name_long,
	external_version,
	gnumed_revision,
	engine,
	filename,
	edit_after_substitution,
	data
) values (
	(select pk from ref.form_types where name = 'current medication list'),
	'current medication list',
	'MedPlan AMTS (~2.3, D)',
	'Medikationsplan AMTS (~2.3, NICHT konform, Deutschland)',
	'21.8',
	21.8,
	'L',
	'not-amts-med-plan-2_3.tex',
	false,
	'real template missing'::bytea
);

-- --------------------------------------------------------------
delete from ref.paperwork_templates where name_long = 'Medikationsplan AMTS (blanko, ~2.3, NICHT konform, Deutschland)';

insert into ref.paperwork_templates (
	fk_template_type,
	instance_type,
	name_short,
	name_long,
	external_version,
	gnumed_revision,
	engine,
	filename,
	edit_after_substitution,
	data
) values (
	(select pk from ref.form_types where name = 'current medication list'),
	'current medication list',
	'MedPlan AMTS (leer, ~2.3, D)',
	'Medikationsplan AMTS (blanko, ~2.3, NICHT konform, Deutschland)',
	'21.8',
	21.8,
	'L',
	'not-amts-med-plan-2_3-blanko.tex',
	false,
	'real template missing'::bytea
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-AMTS_Medikationsplan-fixup.sql', '21.8');
