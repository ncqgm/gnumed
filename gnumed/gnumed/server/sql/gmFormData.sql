-- ===================================================
-- GnuMed forms data related tables

-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>
-- license: GPL
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/Attic/gmFormData.sql,v $
-- $Revision: 1.3 $
-- ===================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================
-- form instance tables
-- ===================================================
create table form_instances (
	id serial primary key,
	id_transaction integer references clinical_transaction (id),
	id_form integer references form_types (id),
	venue varchar(10)
);

-- should be normalized, really
comment on column form_instance.venue is
	'how did we use this form instance, eg. "not yet", "printed", "faxed", "emailed", "stored on smartcard", ...';

-- ===================================================
create table form_fields_filled (
	id serial primary key,
	id_form_instance integer references form_instances(id),
	id_field_type integer references form_fields (id),
	value varchar(256)
);

-- =============================================
-- do simple schema revision tracking
\i gmSchemaRevision.sql
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmFormData.sql,v $', '$Revision: 1.3 $');

-- =============================================
-- $Log: gmFormData.sql,v $
-- Revision 1.3  2003-01-05 13:05:51  ncq
-- - schema_revision -> gm_schema_revision
--
-- Revision 1.2  2003/01/01 01:01:39  ncq
-- - form_instances.venue added
--
-- Revision 1.1  2002/12/31 23:01:19  ncq
-- - original check in
--
