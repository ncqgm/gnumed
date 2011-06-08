-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v11-blobs-lnk_hospital_stay-static.sql,v 1.1 2009-04-01 15:57:07 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table blobs.lnk_doc2hospital_stay (
	pk serial primary key,
	fk_stay integer
		references clin.hospital_stay(pk)
			on update cascade
			on delete restrict,
	fk_document integer
		references blobs.doc_med(pk)
			on update cascade
			on delete restrict
) inherits (audit.audit_fields);

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-blobs-lnk_hospital_stay-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v11-blobs-lnk_hospital_stay-static.sql,v $
-- Revision 1.1  2009-04-01 15:57:07  ncq
-- - new
--
--