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
drop index if exists dem.idx_dem_names_id_identity cascade;
create index idx_dem_names_id_identity on dem.names(id_identity);


-- lastnames
drop index if exists dem.idx_dem_names_last cascade;
drop index if exists dem.idx_dem_names_lastnames cascade;
create index idx_dem_names_lastnames on dem.names(lastnames);

drop index if exists dem.idx_dem_names_last_lower cascade;
drop index if exists dem.idx_dem_names_lastnames_lower cascade;
create index idx_dem_names_lastnames_lower on dem.names (lower(lastnames));

drop index if exists dem.idx_dem_names_last_trgm cascade;
drop index if exists dem.idx_dem_names_lastnames_trgm cascade;
create index idx_dem_names_lastnames_trgm on dem.names using gin (lastnames pgtrgm.gin_trgm_ops);


-- firstnames
drop index if exists dem.idx_names_firstnames cascade;
drop index if exists dem.idx_dem_names_firstnames cascade;
create index idx_dem_names_firstnames on dem.names (firstnames);

drop index if exists dem.idx_dem_names_firstnames_lower cascade;
create index idx_dem_names_firstnames_lower on dem.names (lower(firstnames));

drop index if exists dem.idx_dem_names_first_trgm cascade;
drop index if exists dem.idx_dem_names_firstnames_trgm cascade;
create index idx_dem_names_firstnames_trgm on dem.names using gin (firstnames pgtrgm.gin_trgm_ops);


-- active names
drop index if exists dem.idx_dem_names_active_names cascade;
create index idx_dem_names_active_names on dem.names (id_identity, active) WHERE active IS TRUE;

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-dem-names-idx.sql', '22.25');
