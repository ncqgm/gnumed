-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v11-ref-data_source-dynamic.sql,v 1.1 2009-06-10 20:57:45 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop index idx_ref_data_source_lang cascade;
\set ON_ERROR_STOP 1

create index idx_ref_data_source_lang on ref.data_source(lang);

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-ref-data_source-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v11-ref-data_source-dynamic.sql,v $
-- Revision 1.1  2009-06-10 20:57:45  ncq
-- - better indexes
--
--