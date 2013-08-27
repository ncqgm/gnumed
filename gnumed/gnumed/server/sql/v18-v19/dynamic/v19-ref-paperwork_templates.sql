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
-- Check: ref.paperwork_templates_engine_check (add H: HTML and S: XSLT as possible values)'

ALTER TABLE ref.paperwork_templates DROP CONSTRAINT if exists engine_range;
ALTER TABLE ref.paperwork_templates DROP CONSTRAINT if exists ref_templates_engine_range;

ALTER TABLE ref.paperwork_templates
	ADD CONSTRAINT ref_templates_engine_range CHECK (
		engine = ANY(ARRAY['T'::text, 'L'::text, 'H'::text, 'O'::text, 'I'::text, 'G'::text, 'P'::text, 'A'::text, 'X'::text, 'S'::text])
	);

COMMENT ON COLUMN ref.paperwork_templates.engine IS 'the business layer forms engine used to process this form,
	currently:
	- T: plain text (generic postprocessing)
	- L: LaTeX
	- H: HTML
	- O: OpenOffice
	- I: image editor (visual progress notes)
	- G: gnuplot scripts (test results graphing)
	- P: PDF form (FDF based)
	- A: AbiWord
	- X: Xe(La)TeX
	- S: XSLT';

-- --------------------------------------------------------------
-- .edit_after_substitution
comment on column ref.paperwork_templates.edit_after_substitution is
	'Whether to offer last-minute, manual, generic editing inbetween placeholder substitution and final output generation.';

alter table ref.paperwork_templates
	alter column edit_after_substitution
		set default True;

update ref.paperwork_templates
set edit_after_substitution = True
where edit_after_substitution is null;

alter table ref.paperwork_templates
	alter column edit_after_substitution
		set not null;

-- --------------------------------------------------------------
-- ref.v_paperwork_templates
\unset ON_ERROR_STOP
drop view ref.v_paperwork_templates cascade;
\set ON_ERROR_STOP 1


create view ref.v_paperwork_templates as
select
	pk
		as pk_paperwork_template,
	name_short,
	name_long,
	external_version,
	(select name from ref.form_types where pk = fk_template_type)
		as template_type,
	(select _(name) from ref.form_types where pk = fk_template_type)
		as l10n_template_type,
	coalesce(instance_type, (select name from ref.form_types where pk = fk_template_type))
		as instance_type,
	coalesce(_(instance_type), (select _(name) from ref.form_types where pk = fk_template_type))
		as l10n_instance_type,
	engine,
	in_use,
	edit_after_substitution,
	filename,
	case
		when data is not NULL then True
		else False
	end
		as has_template_data,
--	(select exists(select 1 from public.form_fields where fk_form = r_pt.pk limit 1))
--		as has_instances,
	modified_when
		as last_modified,
	coalesce (
		(select short_alias from dem.staff where db_user = r_pt.modified_by),
		'<' || r_pt.modified_by || '>'
	) as modified_by,
	fk_template_type
		as pk_template_type,
	xmin
		as xmin_paperwork_template
from
	ref.paperwork_templates r_pt
;


grant select on
	ref.v_paperwork_templates
to group "gm-doctors";

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
