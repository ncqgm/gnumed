-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
drop table if exists ref.atc_group cascade;
drop table if exists audit.log_atc_group cascade;

drop table if exists ref.atc_substance cascade;
drop table if exists audit.log_atc_substance cascade;

-- --------------------------------------------------------------
create table ref.atc_staging (
	atc text,
    name text,
	ddd text,
    unit text,
    adro text,
    comment text
);

-- --------------------------------------------------------------
create table ref.atc (
	pk serial primary key,
	-- .code <- atc
	-- .term <- name
	ddd numeric,
	unit text,
	administration_route text
	-- .comment
) inherits (ref.coding_system_root);

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-ref-atc-static.sql,v $', '$Revision: 1.1 $');
