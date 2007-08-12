-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v6
-- Target database version: v7
--
-- License: GPL
-- Author: 
-- 
-- ==============================================================
-- $Id: ref-form_tables.sql,v 1.4 2007-08-12 00:18:38 ncq Exp $
-- $Revision: 1.4 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on table ref.form_types is
	'types of forms which are available, generally by purpose
	 (radiology, pathology, sick leave, Therapiebericht etc.)';

select audit.add_table_for_audit('ref', 'form_defs');


comment on table ref.form_defs is
	'form definitions';
comment on column ref.form_defs.document_type is
	'default document type to store documents generated from this form under\n,
note that this may generate rows in blobs.doc_type if\n
set to a non-existant document type';
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


-- example form template
\unset ON_ERROR_STOP
insert into ref.form_types (name) values (i18n.i18n('physical therapy report'));
\set ON_ERROR_STOP

select i18n.upd_tx('de_DE', 'physical therapy report', 'Therapiebericht (PT)');


--delete from ref.form_defs where name_long = 'Therapiebericht Physiotherapie (GNUmed-Standard)';

insert into ref.form_defs (
	fk_type,
	name_short,
	name_long,
	revision,
	engine,
	template
) values (
	(select pk from ref.form_types where name = 'physical therapy report'),
	'Therapiebericht PT (GNUmed)',
	'Therapiebericht Physiotherapie (GNUmed-Standard)',
	'1.0',
	'O',
	'real template missing,
to create one save an OOo document as a template (.ott) file,
the template can contain "field" -> "placeholders",
the list of known placeholders is in business/gmForms.py::known_placeholders
then import the ott file into the template field in ref.form_defs'::bytea
);


-- --------------------------------------------------------------
grant select, insert, update, insert on
	ref.form_types,
	ref.form_types_pk_seq,
	ref.form_defs,
	ref.form_defs_pk_seq
to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: ref-form_tables.sql,v $', '$Revision: 1.4 $');

-- ==============================================================
-- $Log: ref-form_tables.sql,v $
-- Revision 1.4  2007-08-12 00:18:38  ncq
-- - improved comments
--
-- Revision 1.3  2007/07/22 10:03:28  ncq
-- - add example letter template with instructions
--
-- Revision 1.2  2007/07/22 09:28:42  ncq
-- - missing grants
--
-- Revision 1.1  2007/07/18 14:42:33  ncq
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
