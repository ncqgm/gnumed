-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL
-- Author: 
-- 
-- ==============================================================
-- $Id: ref-form_tables.sql,v 1.1 2007-07-18 14:42:33 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on table ref.form_types is
	'types of forms which are available, generally by purpose
	 (radiology, pathology, sick leave, Therapiebericht etc.)';

select audit.add_table_for_audit('ref', 'form_defs');


comment on table ref.form_defs is
	'form definitions';
comment on column ref.form_defs.name_short is
	'a short name for use in a GUI or some such';
comment on column ref.form_defs.name_long is
	'a long name unambigously describing the form';
comment on column ref.form_defs.revision is
	'GnuMed internal form def version, may
	 occur if we rolled out a faulty form def';
comment on column ref.form_defs.template is
	'the template complete with placeholders in
	 the format accepted by the engine defined in
	 ref.form_defs.engine';
comment on column ref.form_defs.engine is
	'the business layer forms engine used
	 to process this form, currently:
	 - T: plain text
	 - L: LaTeX
	 - H: Health Layer 7
	 - O: OpenOffice';
comment on column ref.form_defs.in_use is
	'whether this template is currently actively
	 used in a given practice';

-- --------------------------------------------------------------
grant select, insert, update, insert on
	ref.form_types,
	ref.form_defs
to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: ref-form_tables.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: ref-form_tables.sql,v $
-- Revision 1.1  2007-07-18 14:42:33  ncq
-- - added for forms handling
--
-- Revision 1.7  2007/05/07 16:32:09  ncq
-- - log_script_insertion() now in gm.
--
-- Revision 1.6  2007/01/27 21:16:08  ncq
-- - the begin/commit does not fit into our change script model
--
-- Revision 1.5  2006/10/24 13:09:45  ncq
-- - What it does duplicates the change log so axe it
--
-- Revision 1.4  2006/09/28 14:39:51  ncq
-- - add comment template
--
-- Revision 1.3  2006/09/18 17:32:53  ncq
-- - make more fool-proof
--
-- Revision 1.2  2006/09/16 21:47:37  ncq
-- - improvements
--
-- Revision 1.1  2006/09/16 14:02:36  ncq
-- - use this as a template for change scripts
--
--
