-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v5
-- Target database version: v6
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: cfg-report_query.sql,v 1.2 2007-04-21 19:42:43 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
select audit.add_table_for_audit('cfg', 'report_query');



comment on table cfg.report_query is
	'This table stores SQL commands to be used in frontend report style queries.';



grant select, insert, update, delete on
	cfg.report_query
	, cfg.report_query_pk_seq
to group "gm-doctors";



\unset ON_ERROR_STOP
alter table cfg.report_query drop constraint "report_query_label_check";
\set ON_ERROR_STOP 1
alter table cfg.report_query
	add check (trim(coalesce(label, 'NULL')) <> '');



\unset ON_ERROR_STOP
alter table cfg.report_query drop constraint "report_query_cmd_check";
\set ON_ERROR_STOP 1
alter table cfg.report_query
	add check (trim(coalesce(cmd, 'NULL')) <> '');



delete from cfg.report_query where label = 'phone list (GNUmed)';
insert into cfg.report_query (label, cmd) values (
	'phone list (GNUmed)',
	'select
	p.lastnames || '', '' || p.firstnames as name,
	p.preferred,
	c.url
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
	date_trunc(''minute'', clin_when),
	narrative
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


-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: cfg-report_query.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: cfg-report_query.sql,v $
-- Revision 1.2  2007-04-21 19:42:43  ncq
-- - add phone list and daily work list reports
--
-- Revision 1.1  2007/04/07 22:30:36  ncq
-- - factored out dynamic part
--
-- Revision 1.1  2007/04/06 23:10:54  ncq
-- - store data mining queries
--
--