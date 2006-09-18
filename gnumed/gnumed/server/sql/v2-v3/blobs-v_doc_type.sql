-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- What it does:
-- - regenerate blobs.v_doc_type
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: blobs-v_doc_type.sql,v 1.1 2006-09-18 17:29:42 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
begin;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view blobs.v_doc_type cascade;
\set ON_ERROR_STOP 1

create view blobs.v_doc_type as
select
	dt.pk as pk_doc_type,
	dt.name as type,
	_(dt.name) as l10n_type,
	dt.xmin as xmin_doc_type
from
	blobs.doc_type dt
;

-- --------------------------------------------------------------
grant select on blobs.v_doc_type to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: blobs-v_doc_type.sql,v $', '$Revision: 1.1 $');

-- --------------------------------------------------------------
commit;

-- ==============================================================
-- $Log: blobs-v_doc_type.sql,v $
-- Revision 1.1  2006-09-18 17:29:42  ncq
-- - drop is_user
--
-- Revision 1.2  2006/09/16 21:47:37  ncq
-- - improvements
--
-- Revision 1.1  2006/09/16 14:02:36  ncq
-- - use this as a template for change scripts
--
--
