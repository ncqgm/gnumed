-- Project: GnuMed
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/country.specific/au/gmDemographics.au.sql,v $
-- $Revision: 1.1 $
-- license: GPL
-- authors: Ian Haywood, Horst Herb, Karsten Hilbert, Richard Terry

-- demographics tables specific für Australia

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
create table org_AU (
	id serial primary key,
	id_org integer unique not null references org(id),
	ACN text
) inherits (audit_mark, audit_fields);

comment on table org_AU is
	'organisation information specific to Australia';
comment on column org_AU.id_org is
	'the organisation this row belongs to';
comment on column org_AU.ACN is
	'Australian Company Number';

create table log_org_AU (
	id integer not null,
	id_org integer not null,
	ACN text
) inherits (audit_trail);

-- ===================================================================
-- do simple schema revision tracking
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmDemographics.au.sql,v $', '$Revision: 1.1 $');

-- ===================================================================
-- $Log: gmDemographics.au.sql,v $
-- Revision 1.1  2003-08-05 09:24:51  ncq
-- - first checkin
--
