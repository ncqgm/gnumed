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
drop index if exists idx_ref_data_source_lang cascade;

create index idx_ref_data_source_lang on ref.data_source(lang);

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-ref-data_source-dynamic.sql,v $', '$Revision: 1.1 $');
