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
		check (engine in ('T', 'L', 'H', 'O', 'I', 'G', 'P', 'A'));


comment on column ref.paperwork_templates.engine is
'the business layer forms engine used to process this form, currently:
	- T: plain text
	- L: LaTeX
	- H: Health Layer 7
	- O: OpenOffice
	- I: image editor (visual progress notes)
	- G: gnuplot scripts (test results graphing)
	- P: PDF form (FDF based)
	- A: AbiWord'
;

-- --------------------------------------------------------------
delete from ref.paperwork_templates where name_long = 'Vaccination history (GNUmed default)';

insert into ref.paperwork_templates (
	fk_template_type,
	name_short,
	name_long,
	external_version,
	engine,
	filename,
	data
) values (
	(select pk from ref.form_types where name = 'Medical statement'),
	'Vacc Hx (GMd)',
	'Vaccination history (GNUmed default)',
	'17.0',
	'L',
	'vaccination-hx.tex',
	'real template missing'::bytea
);

-- --------------------------------------------------------------
delete from ref.paperwork_templates where name_long = 'Vorsorgevollmacht (Bundesministerium für Justiz, Deutschland)';

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
	(select pk from ref.form_types where name = 'pdf form'),
	'other form',
	'Vorsorgevollmacht (D:BMJ)',
	'Vorsorgevollmacht (Bundesministerium für Justiz, Deutschland)',
	'11/2009',
	'P',
	'vorsorgevollmacht-bmj.pdf',
	'real template missing'::bytea
);

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
	'17.0',
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
	'17.0',
	'L',
	'privatrechnung.tex',
	'real template missing'::bytea
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-ref-paperwork_templates.sql', '17.0');
