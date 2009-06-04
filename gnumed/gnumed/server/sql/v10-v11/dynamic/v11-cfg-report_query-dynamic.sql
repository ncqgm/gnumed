-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v11-cfg-report_query-dynamic.sql,v 1.1 2009-06-04 17:47:34 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- fix analysis query
delete from cfg.report_query where label = 'patients whose date of birth may be wrong by one day due to a bug in version 0.4';

insert into cfg.report_query (label, cmd) values (
	'patients whose date of birth may be wrong by one day due to a bug in version 0.4',
'select pk as pk_patient, *
from
	dem.identity
where
	modified_when between (
		-- when was the faulty script imported
		select imported from gm.schema_revision where filename like ''%v10-dem-identity-dynamic.sql%''
	) and (
		-- when was this fixup script imported
		select imported from gm.schema_revision where filename = ''$RCSfile: v11-cfg-report_query-dynamic.sql,v $''
	)
');

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-cfg-report_query-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v11-cfg-report_query-dynamic.sql,v $
-- Revision 1.1  2009-06-04 17:47:34  ncq
-- - first version
--
-- Revision 1.1  2009/05/28 10:44:15  ncq
-- - gm schema_revision is no more
--
--