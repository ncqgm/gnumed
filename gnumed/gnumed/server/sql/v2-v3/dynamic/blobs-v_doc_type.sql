-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- What it does:
-- - regenerate blobs.v_doc_type
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: blobs-v_doc_type.sql,v 1.4 2007-09-24 23:31:17 ncq Exp $
-- $Revision: 1.4 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop view if exists blobs.v_doc_type cascade;

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
