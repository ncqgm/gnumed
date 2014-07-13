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
delete from ref.paperwork_templates where name_long = 'Privatrechnung mit USt. (GNUmed-Vorgabe Deutschland)';

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
	(select pk from ref.form_types where name = 'invoice'),
	'invoice',
	'PKV-Rg (D, mit USt.)',
	'Privatrechnung mit USt. (GNUmed-Vorgabe Deutschland)',
	'20.0',
	'L',
	'privatrechnung.tex',
	'real template missing'::bytea
);

-- --------------------------------------------------------------
delete from ref.paperwork_templates where name_long = 'Privatrechnung ohne USt. (GNUmed-Vorgabe Deutschland)';

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
	(select pk from ref.form_types where name = 'invoice'),
	'invoice',
	'PKV-Rg (D, ohne USt.)',
	'Privatrechnung ohne USt. (GNUmed-Vorgabe Deutschland)',
	'20.0',
	'L',
	'privatrechnung.tex',
	'real template missing'::bytea
);

-- --------------------------------------------------------------
delete from ref.paperwork_templates where name_long = 'Begleitbrief ohne medizinische Daten [K.Hilbert]';

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
	(select pk from ref.form_types where name = 'referral'),
	'sonstiger Arztbrief',
	'Begleitbrf o.med.Ang.[KH]',
	'Begleitbrief ohne medizinische Daten [K.Hilbert]',
	'20.0',
	'L',
	'begleitbrief.tex',
	'real template missing'::bytea
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-ref-paperwork_templates.sql', '20.0');
