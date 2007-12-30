-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-cfg-report_query.sql,v 1.1 2007-12-30 21:06:54 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
delete from cfg.report_query where label = 'patients whose narrative constains a certain coded term';
insert into cfg.report_query (label, cmd) values (
	'patients whose narrative constains a certain coded term',
'select *
from
	dem.v_basic_person
		inner join
	clin.v_coded_item_narrative
		using (pk_identity)
where
	code = ''put the code here''
	-- specify a coding system here
--	and coding_system = ''...''
	-- specify a SOAP category here
--	and soap_cat = ''...''
');


delete from cfg.report_query where label = 'find patients by phone/fax/...';
insert into cfg.report_query (label, cmd) values (
	'find patients by phone/fax/...',
'select *
from
	dem.v_basic_person
		inner join
	dem.v_person_comms
		using (pk_identity)
where
	dem.v_person_comms.url = ''put the URL/number here''
');


delete from cfg.report_query where label = 'find patients by occupation';
insert into cfg.report_query (label, cmd) values (
	'find patients by occupation',
'select *
from
	dem.v_basic_person
		inner join
	dem.v_person_jobs
		using (pk_identity)
where
	dem.v_person_jobs.l10n_occupation = ''put the occupation here''
');

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-cfg-report_query.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v9-cfg-report_query.sql,v $
-- Revision 1.1  2007-12-30 21:06:54  ncq
-- - new
--
--
