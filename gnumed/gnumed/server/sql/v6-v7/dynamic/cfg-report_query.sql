-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v6
-- Target database version: v7
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: cfg-report_query.sql,v 1.2 2007-09-10 13:49:32 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
delete from cfg.report_query where label = 'phone list (GNUmed)';
insert into cfg.report_query (label, cmd) values (
	'phone list (GNUmed)',
	'select
	p.lastnames || '', '' || p.firstnames as name,
	p.preferred as preferred_name,
	c.url as number,
	p.pk_identity as pk_patient
from
	dem.v_basic_person p,
	dem.v_person_comms c
where
	c.pk_identity = p.pk_identity
order by
	lastnames, firstnames'
);



delete from cfg.report_query where label = 'Tagesliste (GNUmed)';
insert into cfg.report_query (label, cmd) values (
	'Tagesliste (GNUmed)',
'select
	date_trunc(''minute'', clin_when) as when,
	narrative,
	pk_patient
from
	clin.v_emr_journal
where
	pk_encounter in (
		-- ecnounters in range:
		select pk_encounter from
			clin.v_pat_encounters
		where
			started between dem.date_trunc_utc(''day'', now()) and now()
	)
	and modified_by like ''%'' || current_user || ''%''
order by clin_when'
);


delete from cfg.report_query where label = 'Happy Birthday list (1 week back and forth from today)';
insert into cfg.report_query (label, cmd) values (
	'Happy Birthday list (1 week back and forth from today)',
'select
	to_char(p.dob, ''DD.TMMonth'') as birthday,
	extract(year from age(dob) - ''10 days''::interval) as age,
	p.lastnames || '', '' || p.firstnames as name,
	p.preferred as preferred_name,
	p.pk_identity as pk_patient
from
	dem.v_basic_person p
where
	dem.dob_is_in_range(p.dob, ''1 week''::interval, ''1 week''::interval) is True
order by
	dob,
	name
');

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: cfg-report_query.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: cfg-report_query.sql,v $
-- Revision 1.2  2007-09-10 13:49:32  ncq
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