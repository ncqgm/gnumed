-- ===================================================================
-- Project: GnuMed - service "Reference" - dynamic objects
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmReference-dynamic.sql,v $
-- $Id: gmReference-dynamic.sql,v 1.1 2005-11-13 17:38:40 ncq Exp $
-- license: GPL
-- author: Karsten Hilbert
-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
-- ref_source --
select add_table_for_audit('ref_source');

comment on table ref_source is
	'lists the available coding systems, classifications, ontologies and term lists';
comment on column ref_source.name_short is
	'shorthand for referrring to this reference entry';
comment on column ref_source.name_long is
	'long, complete (, ?official) name for this reference entry';
comment on column ref_source.version is
	'the exact and non-ambigous version for this entry';
comment on column ref_source.description is
	'optional arbitrary description';
comment on column ref_source.source is
	'non-ambigous description of source; with this info in hand
	 it must be possible to locate a copy of the external reference';

-- lnk_tbl2src --
-- workaround since we cannot add trigger on
-- pg_class directly (and hence not point to
-- it with a foreign key constraint)
select add_x_db_fk_def ('lnk_tbl2src', 'data_table', 'reference', 'pg_class', 'relname');

comment on table lnk_tbl2src is
	'This table links data tables to sources. Source entries may
	 appear more than once (because they describe several tables)
	 but table names must be unique in here. Note, however, that
	 this table only links those data tables to their sources in
	 which all rows have the very same source (such as ICD10).
	 Tables where each row has its own source (say, literature
	 references on diseases etc) will have a column constrained
	 by a foreign key into ref_source directly.';

-- basic_unit --
COMMENT ON TABLE basic_unit IS
	'basic units are SI units, units derived from them and the Unity';

-- unit --
COMMENT ON TABLE unit IS 
	'units as used in real life';
COMMENT ON column unit.fk_basic_unit IS
	'what is the SI-Standard unit for this, e.g. for the unit mg it is kg';
COMMENT ON column unit.factor IS
	'what factor the value with this unit has to be multiplied with to get values in the basic_unit';
COMMENT ON column unit.shift IS
	'what has to be added (after multiplying by factor) to a value with this unit to get values in the basic_unit';

-- atc tables --
select add_table_for_audit('atc_group');
select add_table_for_audit('atc_substance');

-- test_norm --
comment on table test_norm is
	'each row defines one set of measurement reference data';
comment on column test_norm.fk_ref_src is
	'source this reference data set was taken from';
comment on column test_norm.data is
	'the actual reference data in some format,
	 say, XML or like in a *.conf file';

-- papersizes --
comment on column papersizes.size is '(cm, cm)';

-- forms tables --
comment on table form_types is
	'types of forms which are available,
	 generally by purpose (radiology, pathology, sick leave, etc.)';


select add_table_for_audit('form_defs');

comment on table form_defs is
	'form definitions';
comment on column form_defs.name_short is
	'a short name for use in a GUI or some such';
comment on column form_defs.name_long is
	'a long name unambigously describing the form';
comment on column form_defs.revision is
	'GnuMed internal form def version, may
	 occur if we rolled out a faulty form def';
comment on column form_defs.template is
	'the template complete with placeholders in
	 the format accepted by the engine defined in
	 form_defs.engine';
comment on column form_defs.engine is
	'the business layer forms engine used
	 to process this form, currently:
	 - T: plain text
	 - L: LaTeX
	 - H: Health Layer 7';
comment on column form_defs.in_use is
	'whether this template is currently actively
	 used in a given practice';
comment on column form_defs.url is
	'For electronic forms which are always sent to the same 
	url (such as reports to a statutory public-health surveillance
	authority)';
comment on column form_defs.is_user is
	'whether this is an "official" form definition - IOW
	 part of the official GNUmed package and hence installed
	 at install time as opposed to forms defined locally
	 by the user';


comment on table form_fields is
	'List of fields for a particular form';
comment on column form_fields.long_name is
	'The full name of the form field as presented to the user';
comment on column form_fields.template_placeholder is
	'The name of the field as exposed to the form template.
	 In other words, the placeholder in form_defs.template where
	 the value entered into this field ist to be substituted.
	 Must be a valid identifier in the form template''s
	 script language (viz. Python)';
comment on column form_fields.help is
	'longer help text';
comment on column form_fields.fk_type is
	'the field type';
comment on column form_fields.param is
	'a parameter for the field''s behaviour, meaning is type-dependent';
comment on column form_fields.display_order is
	'used to *suggest* display order, but client may ignore';


comment on column form_print_defs.offset_top is
	'in mm - and yes, they do change even within one
	 type of form, but we do not want to change the
	 offset for all the fields in that case';
comment on column form_print_defs.papertype is
	'type of paper such as "watermarked rose",
	 mainly for user interaction on manual_feed==true';

-- ===================================================================
GRANT SELECT ON
	ref_source
	, lnk_tbl2src
	, unit
	, basic_unit
	, test_norm
	, papersizes
	, form_types
	, form_defs
	, form_print_defs
TO GROUP "gm-public";

-- ===================================================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmReference-dynamic.sql,v $', '$Revision: 1.1 $');

-- =============================================
-- $Log: gmReference-dynamic.sql,v $
-- Revision 1.1  2005-11-13 17:38:40  ncq
-- - factor out dynamic DDL
--
--
