-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v11-ref-atc-static.sql,v 1.1 2009-06-04 17:20:39 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop table ref.atc_group cascade;
drop table audit.log_atc_group cascade;

drop table ref.atc_substance cascade;
drop table audit.log_atc_substance cascade;
\set ON_ERROR_STOP 1

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

-- ==============================================================
-- $Log: v11-ref-atc-static.sql,v $
-- Revision 1.1  2009-06-04 17:20:39  ncq
-- - first version
--
--