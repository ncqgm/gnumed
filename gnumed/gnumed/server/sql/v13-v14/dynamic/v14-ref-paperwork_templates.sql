-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
alter table ref.paperwork_templates drop constraint engine_range cascade;
\set ON_ERROR_STOP 1


alter table ref.paperwork_templates
	add constraint engine_range
		check (engine in ('T', 'L', 'H', 'O', 'I', 'G'));


comment on column ref.paperwork_templates.engine is
'the business layer forms engine used to process this form, currently:
	- T: plain text
	- L: LaTeX
	- H: Health Layer 7
	- O: OpenOffice
	- I: image editor (visual progress notes)
	- G: gnuplot scripts (test results graphing)'
;

-- --------------------------------------------------------------
-- visual progress note template type
\unset ON_ERROR_STOP
insert into ref.form_types (name) values (i18n.i18n('gnuplot script'));
\set ON_ERROR_STOP 1

select i18n.upd_tx('de_DE', 'gnuplot script', 'Gnuplot-Script');


-- --------------------------------------------------------------
delete from ref.paperwork_templates where name_long = '2 test types plot script (GNUmed default)';

insert into ref.paperwork_templates (
	fk_template_type,
	name_short,
	name_long,
	external_version,
	engine,
	filename,
	data
) values (
	(select pk from ref.form_types where name = 'gnuplot script'),
	'2 tests plot (GNUmed)',
	'2 test types plot script (GNUmed default)',
	'1.0',
	'G',
	'gm2gpl-plot_2_tests.scr',
	'real template missing'::bytea
);

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v14-ref-paperwork_templates.sql,v $', '$Revision: 1.3 $');
