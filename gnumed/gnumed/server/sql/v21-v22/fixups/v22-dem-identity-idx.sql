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
drop index if exists dem.idx_dem_identity_fk_marital_status cascade;
create index idx_dem_identity_fk_marital_status on dem.identity(fk_marital_status);


drop index if exists dem.idx_dem_identity_fk_emergency_contact cascade;
create index idx_dem_identity_fk_emergency_contact on dem.identity(fk_emergency_contact);


drop index if exists dem.idx_dem_identity_fk_primary_provider cascade;
create index idx_dem_identity_fk_primary_provider on dem.identity(fk_primary_provider);

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-dem-identity-idx.sql', '22.24');
