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
-- $Id: blobs-v_doc_type.sql,v 1.4 2007-09-24 23:31:17 ncq Exp $
-- $Revision: 1.4 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view blobs.v_doc_type cascade;
\set ON_ERROR_STOP 1

create view blobs.v_doc_type as
select
	dt.pk as pk_doc_type,
	dt.name as type,
	_(dt.name) as l10n_type,
	not exists(select 1 from ref.document_type where description=dt.name)
		as is_user_defined,
	exists(select 1 from blobs.doc_med where fk_type=dt.pk)
		as is_in_use,
	dt.xmin as xmin_doc_type
from
	blobs.doc_type dt
;

comment on view blobs.v_doc_type is
	'list active document types, those that are activated for use';

-- --------------------------------------------------------------
grant select on blobs.v_doc_type to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: blobs-v_doc_type.sql,v $', '$Revision: 1.4 $');

-- ==============================================================
-- $Log: blobs-v_doc_type.sql,v $
-- Revision 1.4  2007-09-24 23:31:17  ncq
-- - remove begin; commit; as it breaks the bootstrapper
--
-- Revision 1.3  2006/12/11 17:00:50  ncq
-- - add is_in_use
-- - is_user -> is_user_defined
--
-- Revision 1.2  2006/11/01 12:39:10  ncq
-- - is_user logic was reversed
--
-- Revision 1.1  2006/09/25 10:55:01  ncq
-- - added here
--
-- Revision 1.2  2006/09/19 18:28:40  ncq
-- - virtualize v_doc_type.is_user
--
-- Revision 1.1  2006/09/18 17:29:42  ncq
-- - drop is_user
--
-- Revision 1.2  2006/09/16 21:47:37  ncq
-- - improvements
--
-- Revision 1.1  2006/09/16 14:02:36  ncq
-- - use this as a template for change scripts
--
--
