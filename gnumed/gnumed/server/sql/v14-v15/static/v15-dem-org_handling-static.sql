-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- dem.org_category
alter table dem.org_category
	rename column id to pk;

-- --------------------------------------------------------------
-- dem.org

-- rename old table
alter table dem.org
	rename to org_old;


-- create new table inheriting from audit root
create table dem.org (
	pk serial primary key,
	description text,
	fk_category integer
) inherits (audit.audit_fields);


-- move data over
insert into dem.org (
	fk_category,
	description
) select
	id_category,
	description
from
	dem.org_old
;


-- remove old table
drop table dem.org_old cascade;

-- --------------------------------------------------------------
-- dem.org_unit
create table dem.org_unit (
	pk serial primary key,
	description text,
	fk_org integer,
	fk_address integer,
	fk_category integer
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
-- dem.lnk_org_unit2comm
create table dem.lnk_org_unit2comm (
	pk serial primary key,
	fk_org_unit integer,
	url text,
	fk_type integer,
	is_confidential boolean
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
-- dem.lnk_org_unit2ext_id
create table dem.lnk_org_unit2ext_id (
	pk serial primary key,
	fk_org_unit integer,
	external_id text,
	fk_type integer,
	comment text
) inherits (audit.audit_fields);

-- --------------------------------------------------------------

drop table dem.lnk_org2comm cascade;
drop table dem.lnk_org2ext_id cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-dem-org_handling-static.sql', 'Revision: 1.10');

-- ==============================================================
