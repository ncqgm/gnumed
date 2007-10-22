-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v7
-- Target database version: v8
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: cfg-report_query.sql,v 1.1 2007-10-22 11:41:13 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
delete from cfg.report_query where label = 'Happy Birthday list (this month)';
insert into cfg.report_query (label, cmd) values (
	'Happy Birthday list (this month)',
'select
	extract(year from age(dob)) as age_now,
	to_char(p.dob, ''DD.TMMonth YYYY'') as birthday,
	p.lastnames || '', '' || p.firstnames as name,
	p.preferred as preferred_name,
	p.pk_identity as pk_patient
from
	dem.v_basic_person p
where
	date_part(''month'', p.dob) = date_part(''month'', now())
order by
	date_part(''day'', p.dob),
	name
');

delete from cfg.report_query where label = 'Happy Birthday list (next month)';
insert into cfg.report_query (label, cmd) values (
	'Happy Birthday list (next month)',
'select
	extract(year from age(dob)) as age_now,
	to_char(p.dob, ''DD.TMMonth YYYY'') as birthday,
	p.lastnames || '', '' || p.firstnames as name,
	p.preferred as preferred_name,
	p.pk_identity as pk_patient
from
	dem.v_basic_person p
where
	date_part(''month'', p.dob) = (date_part(''month'', now()) + 1)
order by
	date_part(''day'', p.dob),
	name
');

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: cfg-report_query.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: cfg-report_query.sql,v $
-- Revision 1.1  2007-10-22 11:41:13  ncq
-- - add birtday list this/next month
--
-- Revision 1.3  2007/09/20 21:30:52  ncq
-- - grants for cfg.db_logon_banner
--
-- Revision 1.2  2007/09/10 13:49:32  ncq
-- - add birthday list report
--
-- Revision 1.1  2007/08/24 15:59:57  ncq
-- - fix example queries to allow for patient callup
--
-- Revision 1.3  2007/05/07 16:33:06  ncq
-- - log_script_insertion() now in gm.
--
-- Revision 1.2  2007/04/21 19:42:43  ncq
-- - add phone list and daily work list reports
--
-- Revision 1.1  2007/04/07 22:30:36  ncq
-- - factored out dynamic part
--
-- Revision 1.1  2007/04/06 23:10:54  ncq
-- - store data mining queries
--
--