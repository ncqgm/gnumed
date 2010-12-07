-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- example referral template
\unset ON_ERROR_STOP
insert into ref.form_types (name) values (i18n.i18n('EMR printout'));
\set ON_ERROR_STOP 1

select i18n.upd_tx('de_DE', 'EMR printout', 'Karteiausdruck');

delete from ref.paperwork_templates where name_long = 'EMR Journal (GNUmed default)';

insert into ref.paperwork_templates (
	fk_template_type,
	name_short,
	name_long,
	external_version,
	engine,
	filename,
	data
) values (
	(select pk from ref.form_types where name = 'EMR printout'),
	'EMR Journal (GNUmed)',
	'EMR Journal (GNUmed default)',
	'1.0',
	'L',
	'emr-journal.tex',
	'real template missing'::bytea
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-ref-paperwork_templates.sql', 'Revision: 1.3');
