-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-clin-incoming_data_unmatch-static2.sql,v 1.1 2008-08-21 10:20:37 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.incoming_data_unmatched
	add column external_data_id text;
alter table clin.incoming_data_unmatched
	add column fk_identity_disambiguated integer;

alter table audit.log_incoming_data_unmatched
	add column external_data_id text;
alter table audit.log_incoming_data_unmatched
	add column fk_identity_disambiguated integer;


alter table clin.incoming_data_unmatchable
	add column external_data_id text;
alter table clin.incoming_data_unmatchable
	add column fk_identity_disambiguated integer;

alter table audit.log_incoming_data_unmatchable
	add column external_data_id text;
alter table audit.log_incoming_data_unmatchable
	add column fk_identity_disambiguated integer;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-clin-incoming_data_unmatch-static2.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v9-clin-incoming_data_unmatch-static2.sql,v $
-- Revision 1.1  2008-08-21 10:20:37  ncq
-- - add .external_data_id and .fk_identity_disambiguated
--
-- Revision 1.2  2008/02/29 23:55:17  ncq
-- - later audit logs, too
--
-- Revision 1.1  2008/02/26 16:20:58  ncq
-- - add gender/requestor
--
--
