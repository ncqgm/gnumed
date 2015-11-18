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
-- ref.v_paperwork_templates
drop view if exists ref.v_paperwork_templates cascade;


create view ref.v_paperwork_templates as
select
	r_pt.pk
		as pk_paperwork_template,
	r_pt.name_short,
	r_pt.name_long,
	r_pt.external_version,
	r_pt.gnumed_revision,
	(select r_ft.name from ref.form_types r_ft where r_ft.pk = r_pt.fk_template_type)
		as template_type,
	(select _(r_ft.name) from ref.form_types r_ft where r_ft.pk = r_pt.fk_template_type)
		as l10n_template_type,
	coalesce(r_pt.instance_type, (select r_ft.name from ref.form_types r_ft where r_ft.pk = r_pt.fk_template_type))
		as instance_type,
	coalesce(_(r_pt.instance_type), (select _(r_ft.name) from ref.form_types r_ft where r_ft.pk = r_pt.fk_template_type))
		as l10n_instance_type,
	r_pt.engine,
	r_pt.in_use,
	r_pt.edit_after_substitution,
	r_pt.filename,
	case
		when r_pt.data is not NULL then True
		else False
	end
		as has_template_data,
--	(select exists(select 1 from public.form_fields where fk_form = r_pt.pk limit 1))
--		as has_instances,
	r_pt.modified_when
		as last_modified,
	coalesce (
		(select d_s.short_alias from dem.staff d_s where d_s.db_user = r_pt.modified_by),
		'<' || r_pt.modified_by || '>'
	) as modified_by,
	r_pt.fk_template_type
		as pk_template_type,
	r_pt.xmin
		as xmin_paperwork_template
from
	ref.paperwork_templates r_pt
;


grant select on
	ref.v_paperwork_templates
to group "gm-doctors";

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
