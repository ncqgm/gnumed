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
\unset ON_ERROR_STOP
alter table ref.paperwork_templates drop constraint engine_range cascade;
\set ON_ERROR_STOP 1


alter table ref.paperwork_templates
	add constraint engine_range
		check (engine in ('T', 'L', 'H', 'O', 'I', 'G', 'P', 'A', 'X'));


comment on column ref.paperwork_templates.engine is
'the business layer forms engine used to process this form, currently:
	- T: plain text (generic postprocessing)
	- L: LaTeX
	- H: Health Layer 7
	- O: OpenOffice
	- I: image editor (visual progress notes)
	- G: gnuplot scripts (test results graphing)
	- P: PDF form (FDF based)
	- A: AbiWord
	- X: Xe(La)TeX'
;

-- --------------------------------------------------------------
delete from ref.paperwork_templates where name_long = 'ungültiges GKV-Rezept (GNUmed-Vorgabe)';

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
	'ungültiges GKV-Rpt (GMd)',
	'ungültiges GKV-Rezept (GNUmed-Vorgabe)',
	'v18.0',
	'L',
	'form-header.tex',
	'real template missing'::bytea
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-ref-paperwork_templates.sql', '18.0');
