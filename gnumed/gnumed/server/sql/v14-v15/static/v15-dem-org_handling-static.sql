-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
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
-- dem.lnk_org2comm

alter table dem.lnk_org2comm
	rename column id to pk;


alter table dem.lnk_org2comm
	rename column id_org to fk_org;


alter table dem.lnk_org2comm
	rename column id_type to fk_type;

-- --------------------------------------------------------------
-- dem.lnk_org2ext_id

alter table dem.lnk_org2ext_id
	rename column id to pk;


alter table dem.lnk_org2ext_id
	rename column id_org to fk_org;


alter table dem.lnk_org2ext_id
	rename column fk_origin to fk_type;

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
select gm.log_script_insertion('$RCSfile: zzz-template.sql,v $', '$Revision: 1.10 $');

-- ==============================================================
