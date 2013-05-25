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
delete from ref.paperwork_templates where name_long = 'Grünes Rezept (DE, GNUmed-Vorgabe)';

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
	(select pk from ref.form_types where name = 'prescription'),
	'prescription',
	'Rpt Grün (GMd)',
	'Grünes Rezept (DE, GNUmed-Vorgabe)',
	'19.0',
	'L',
	'form-header.tex',
	'real template missing'::bytea
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-ref-paperwork_templates.sql', '19.0');
