-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: v12-ref-paperwork_templates.sql,v 1.2 2009-12-30 18:48:36 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- example form template
\unset ON_ERROR_STOP
insert into ref.form_types (name) values (i18n.i18n('current medication list'));
\set ON_ERROR_STOP 1

select i18n.upd_tx('de_DE', 'current medication list', 'Medikamentenliste');

delete from ref.paperwork_templates where name_long = 'Current medication list (GNUmed default)';

insert into ref.paperwork_templates (
	fk_template_type,
	name_short,
	name_long,
	external_version,
	engine,
	filename,
	data
) values (
	(select pk from ref.form_types where name = 'current medication list'),
	'Medication list (GNUmed)',
	'Current medication list (GNUmed default)',
	'1.0',
	'L',
	'medslist.tex',
	'real template missing'::bytea
);

-- --------------------------------------------------------------
delete from public.form_fields where
	fk_form = (select pk from ref.paperwork_templates where name_long = 'Standard specialist referral letter for AU');

delete from ref.paperwork_templates where name_long = 'Standard specialist referral letter for AU';



delete from public.form_fields where
	fk_form = (select pk from ref.paperwork_templates where name_long = 'Prescription using the standard form of the Pharmaceutical Benefits Scheme');

delete from ref.paperwork_templates where name_long = 'Prescription using the standard form of the Pharmaceutical Benefits Scheme';



delete from public.form_fields where
	fk_form = (select pk from ref.paperwork_templates where name_long = 'A proof-of-concept basic request form');

delete from ref.paperwork_templates where name_long = 'A proof-of-concept basic request form';

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-ref-paperwork_templates.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v12-ref-paperwork_templates.sql,v $
-- Revision 1.2  2009-12-30 18:48:36  ncq
-- - remove the confusing previous LaTeX templates
--
-- Revision 1.1  2009/12/22 11:52:46  ncq
-- - medication list template skeleton
--
--