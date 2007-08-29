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
-- $Id: ref-form_tables.sql,v 1.7 2007-08-29 14:46:23 ncq Exp $
-- $Revision: 1.7 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on table ref.form_types is
	'types of forms which are available, generally by purpose
	 (radiology, pathology, sick leave, Therapiebericht etc.)';

-- --------------------------------------------------------------
select audit.add_table_for_audit('ref', 'paperwork_templates');


comment on table ref.paperwork_templates is
	'form and letter template definitions';
comment on column ref.paperwork_templates.instance_type is
	'default document type to store documents generated from
	 this form under, note that this may generate rows in
	 blobs.doc_type if set to a non-existant document type';
comment on column ref.paperwork_templates.name_short is
	'a short name for use in a GUI or some such';
comment on column ref.paperwork_templates.name_long is
	'a long name unambigously describing the form';
comment on column ref.paperwork_templates.gnumed_revision is
	'GnuMed internal form def version, may
	 occur if we rolled out a faulty form def';
comment on column ref.paperwork_templates.data is
	'the template complete with placeholders in
	 the format accepted by the engine defined in
	 ref.paperwork_templates.engine';
comment on column ref.paperwork_templates.engine is
	'the business layer forms engine used
	 to process this form, currently:
	 - T: plain text
	 - L: LaTeX
	 - H: Health Layer 7
	 - O: OpenOffice';
comment on column ref.paperwork_templates.in_use is
	'whether this template is currently actively
	 used in a given practice';
comment on column ref.paperwork_templates.filename is
	'the filename from when the template data was imported if applicable,
	 used by some engines (such as OOo) to differentiate what to do
	 with certain files, such as *.ott vs. *.ods, GNUmed uses it
	 to derive a file extension when exporting the template data';


-- UPDATE
create or replace function ref.trf_protect_template_data()
	returns trigger
	language 'plpgsql'
	as '
BEGIN
	if NEW.data != OLD.data then
		-- look for references in public.form_fields
		select * from public.form_fields where fk_form = NEW.pk;
		if FOUND then
			raise exception ''Updating ref.paperwork_templates.data not allowed because it is referenced from existing forms.'';
		end if;
	end if;
	return NEW;
END;';

comment on function ref.trf_protect_template_data() is
	'Do not allow updates to the template data if
	 any forms already use this template.';

create trigger tr_protect_template_data
	before update on ref.paperwork_templates
	for each row execute procedure ref.trf_protect_template_data()
;


-- example form template
\unset ON_ERROR_STOP
insert into ref.form_types (name) values (i18n.i18n('physical therapy report'));
\set ON_ERROR_STOP 1

select i18n.upd_tx('de_DE', 'physical therapy report', 'Therapiebericht (PT)');

delete from ref.paperwork_templates where name_long = 'Therapiebericht Physiotherapie (GNUmed-Standard)';

insert into ref.paperwork_templates (
	fk_template_type,
	name_short,
	name_long,
	external_version,
	engine,
	filename,
	data
) values (
	(select pk from ref.form_types where name = 'physical therapy report'),
	'Therapiebericht PT (GNUmed)',
	'Therapiebericht Physiotherapie (GNUmed-Standard)',
	'1.0',
	'O',
	'template.ott',
	'real template missing,
to create one save an OOo document as a template (.ott) file,
the template can contain "field" -> "placeholders",
the list of known placeholders is in business/gmForms.py::known_placeholders
then import the ott file into the template field in ref.paperwork_templates'::bytea
);


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
	filename,
	modified_when
		as last_modified,
	fk_template_type
		as pk_template_type,
	xmin
		as xmin_paperwork_template
from
	ref.paperwork_templates
;

-- --------------------------------------------------------------
grant select, insert, update, insert on
	ref.form_types,
	ref.form_types_pk_seq,
	ref.paperwork_templates,
	ref.paperwork_templates_pk_seq
to group "gm-doctors";

grant select on
	ref.v_paperwork_templates
to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: ref-form_tables.sql,v $', '$Revision: 1.7 $');

-- ==============================================================
-- $Log: ref-form_tables.sql,v $
-- Revision 1.7  2007-08-29 14:46:23  ncq
-- - revision -> gnumed_revision, version -> external_version
-- - remove data_md5
-- - adjust triggers on ref.paperwork_templates
--
-- Revision 1.6  2007/08/20 14:35:32  ncq
-- - form_defs -> paperwork_templates
-- - rename columns, add triggers on insert/update
-- - enhanced v_paperwork_templates
--
-- Revision 1.5  2007/08/13 22:09:00  ncq
-- - ref.form_defs.filename
-- - ref.v_form_defs
--
-- Revision 1.4  2007/08/12 00:18:38  ncq
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
