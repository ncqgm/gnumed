-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v11-clin-current_medication-static.sql,v 1.5 2009-08-08 10:45:19 ncq Exp $
-- $Revision: 1.5 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop table audit.log_clin_medication;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table clin.substance_brand (
	pk serial primary key,
	description text,
	preparation text,
	atc_code text,
	is_fake boolean
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
create table clin.active_substance (
	pk serial primary key,
	description text,
	atc_code text
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
create table clin.substance_intake (
	pk serial primary key,
	fk_brand integer
		references clin.substance_brand(pk)
			on update cascade
			on delete restrict,
	fk_substance integer
		references clin.active_substance(pk)
			on update cascade
			on delete restrict,
	strength text,
	preparation text,
	schedule text,
	aim text,
--	notes text,			-> .narrative
--	started date,		-> .clin_when
	duration interval,
	intake_is_approved_of boolean
) inherits (clin.clin_root_item);

-- --------------------------------------------------------------
create table clin.lnk_substance2episode (
	pk serial primary key,
	fk_episode integer
		references clin.episode(pk)
			on update cascade
			on delete restrict,
	fk_substance integer
		references clin.substance_intake(pk)
			on update cascade
			on delete restrict
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-clin-current_medication-static.sql,v $', '$Revision: 1.5 $');

-- ==============================================================
-- $Log: v11-clin-current_medication-static.sql,v $
-- Revision 1.5  2009-08-08 10:45:19  ncq
-- - fix drop which was missing a table keyword
--
-- Revision 1.4  2009/06/04 16:37:57  ncq
-- - intake-is-approved-of
--
-- Revision 1.3  2009/05/12 12:09:41  ncq
-- - improved layout
--
-- Revision 1.2  2009/05/04 15:05:59  ncq
-- - better naming
--
-- Revision 1.1  2009/05/04 11:39:26  ncq
-- - new
--
--