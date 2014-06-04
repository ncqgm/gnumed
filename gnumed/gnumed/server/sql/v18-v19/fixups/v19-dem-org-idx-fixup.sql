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
drop index if exists dem.idx_dem_org_fk_category cascade;
create index idx_dem_org_fk_category on dem.org(fk_category);

-- --------------------------------------------------------------
drop index if exists dem.idx_dem_org_unit_fk_category cascade;
create index idx_dem_org_unit_fk_category on dem.org_unit(fk_category);

drop index if exists dem.idx_dem_org_unit_fk_address cascade;
create index idx_dem_org_unit_fk_address on dem.org_unit(fk_address);

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-dem-org-idx-fixup.sql', '19.9');
