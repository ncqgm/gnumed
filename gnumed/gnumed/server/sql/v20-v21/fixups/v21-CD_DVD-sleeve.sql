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
delete from ref.paperwork_templates where name_long = 'CD/DVD sleeve [K.Hilbert]';

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
	(select pk from ref.form_types where name = 'other letter'),
	'other letter',
	'CD/DVD sleeve',
	'CD/DVD sleeve [K.Hilbert]',
	'21.7',
	'L',
	'gm-cd_dvd-sleeve.tex',
	false,
	'real template missing'::bytea
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-CD_DVD-sleeve.sql', '21.7');
