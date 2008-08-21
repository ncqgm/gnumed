-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-clin-incoming_data_unmatch-dynamic.sql,v 1.1 2008-08-21 10:21:11 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.incoming_data_unmatched add foreign key (fk_identity_disambiguated)
	references dem.identity(pk)
	on update cascade
	on delete restrict;


comment on column clin.incoming_data_unmatched.gender is
	'Gender of patient in source data if available.';

comment on column clin.incoming_data_unmatched.requestor is
	'Requestor of data (e.g. who ordered test results) if available in source data.';

comment on column clin.incoming_data_unmatched.external_data_id is
	'ID of content of .data in external system (e.g. importer) where appropriate';

comment on column clin.incoming_data_unmatched.fk_identity_disambiguated is
	'ID of patient the data is judged to really belong to.';

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-clin-incoming_data_unmatch-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v9-clin-incoming_data_unmatch-dynamic.sql,v $
-- Revision 1.1  2008-08-21 10:21:11  ncq
-- - foreign key and comments
--
--