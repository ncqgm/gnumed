-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table ref.atc
	rename to atc_inherited;

-- --------------------------------------------------------------
create table ref.atc (
	pk serial primary key,
	code text,
	term text,
	fk_data_source integer,
	ddd numeric,
	unit text,
	administration_route text
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-ref-atc-static.sql', '1.0');
