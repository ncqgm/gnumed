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
delete from ref.paperwork_templates where name_long = 'Upcoming Recalls (GNUmed default)';

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
	(select pk from ref.form_types where name = 'reminder'),
	'Medical statement',
	'Recalls (GMd)',
	'Upcoming Recalls (GNUmed default)',
	'18.3',
	'L',
	'recalls.tex',
	'real template missing'::bytea
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-ref-recalls_template-fixup.sql', '18.3');
