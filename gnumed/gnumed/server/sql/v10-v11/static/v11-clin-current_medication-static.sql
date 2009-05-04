-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v11-clin-current_medication-static.sql,v 1.1 2009-05-04 11:39:26 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop audit.log_clin_medication;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table clin.drug_brand (
	pk serial primary key,
	description text,
	preparation text,
	is_fake boolean
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
create table clin.drug_component (
	pk serial primary key,
	fk_brand integer
		references clin.drug_brand(pk)
			on update cascade
			on delete restrict,
	description text,
	atc_code text,
	strength text
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
create table clin.current_medication (
	pk serial primary key,
	fk_brand integer
		references clin.drug_brand(pk)
			on update cascade
			on delete restrict,
	schedule text,
	aim text,
--	notes text,			-> .narrative
--	started date,		-> .clin_when
	duration interval
) inherits (clin.clin_root_item);

-- --------------------------------------------------------------
create table clin.lnk_medication2episode (
	pk serial primary key,
	fk_episode integer
		references clin.episode(pk)
			on update cascade
			on delete restrict,
	fk_medication integer
		references clin.current_medication(pk)
			on update cascade
			on delete restrict
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-clin-current_medication-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v11-clin-current_medication-static.sql,v $
-- Revision 1.1  2009-05-04 11:39:26  ncq
-- - new
--
--