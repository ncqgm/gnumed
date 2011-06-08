-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v11-ref-loinc-dynamic.sql,v 1.1 2009-04-19 21:54:02 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
comment on table ref.loinc_staging is
'used for importing LOINC data, columns correspond 1:1 with the LOINC CSV file fields';

-- --------------------------------------------------------------
comment on table ref.loinc is
'holds LOINC codes';

comment on column ref.loinc.code is
'holds LOINC_NUM';

comment on column ref.loinc.term is
'holds either long_common_name or a ":".join of .component to .method_type';

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-ref-loinc-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v11-ref-loinc-dynamic.sql,v $
-- Revision 1.1  2009-04-19 21:54:02  ncq
-- - new
--
--