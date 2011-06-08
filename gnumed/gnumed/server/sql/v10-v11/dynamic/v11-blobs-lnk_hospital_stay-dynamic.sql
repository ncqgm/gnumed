-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v11-blobs-lnk_hospital_stay-dynamic.sql,v 1.1 2009-04-01 15:57:26 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on table blobs.lnk_doc2hospital_stay is
'links documents to any hospital stay they might pertain to';

alter table blobs.lnk_doc2hospital_stay
	add constraint unique_stay_per_document
		unique(fk_document)
;



alter table blobs.lnk_doc2hospital_stay
	alter column fk_stay
		set not null;



alter table blobs.lnk_doc2hospital_stay
	alter column fk_document
		set not null;

-- --------------------------------------------------------------
grant select, insert, update, delete on
	blobs.lnk_doc2hospital_stay
	, blobs.lnk_doc2hospital_stay_pk_seq
to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-blobs-lnk_hospital_stay-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v11-blobs-lnk_hospital_stay-dynamic.sql,v $
-- Revision 1.1  2009-04-01 15:57:26  ncq
-- - new
--
--