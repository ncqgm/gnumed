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
delete from ref.paperwork_templates where name_long = 'Begleitbrief mit Diagnosen [K.Hilbert]';

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
	'Begleitbrf m.Dg.[KH]',
	'Begleitbrief mit Diagnosen [K.Hilbert]',
	'22.4',
	'L',
	'begleitbrief.tex',
	'real template missing'::bytea
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-ref-paperwork_templates-fixups.sql', '22.4');
