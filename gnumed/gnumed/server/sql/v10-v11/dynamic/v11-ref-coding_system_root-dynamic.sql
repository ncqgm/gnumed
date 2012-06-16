-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v11-ref-coding_system_root-dynamic.sql,v 1.1 2009-06-10 20:55:44 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop index idx_coding_sys_root_fk_data_src cascade;
\set ON_ERROR_STOP 1


create index idx_coding_sys_root_fk_data_src on ref.coding_system_root(fk_data_source);


\unset ON_ERROR_STOP 1
alter table ref.coding_system_root
	drop constraint code_unique_per_system cascade;

alter table ref.coding_system_root
	drop constraint term_unique_per_system cascade;

alter table ref.coding_system_root
	drop constraint coding_system_root_fk_data_source_key cascade;

alter table ref.coding_system_root
	drop constraint coding_system_root_fk_data_source_key1 cascade;
\set ON_ERROR_STOP 1


alter table ref.coding_system_root
	add constraint code_unique_per_system unique (code, fk_data_source);

alter table ref.coding_system_root
	add constraint term_unique_per_system unique (term, fk_data_source);

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-ref-coding_system_root-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v11-ref-coding_system_root-dynamic.sql,v $
-- Revision 1.1  2009-06-10 20:55:44  ncq
-- - improved indexing
--
--