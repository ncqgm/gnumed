-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: clin-health_issue.sql,v 1.2 2006-12-11 17:02:46 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop index clin.idx_health_issue_modified_by;
\set ON_ERROR_STOP 1

create index idx_health_issue_modified_by on clin.health_issue(modified_by);

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop function clin.f_announce_h_issue_mod() cascade;
drop function audit.trf_announce_h_issue_mod() cascade;
\set ON_ERROR_STOP 1

create function audit.trf_announce_h_issue_mod()
	returns trigger
	language 'plpgsql'
	as '
declare
	patient_pk integer;
begin
	-- get patient ID
	if TG_OP = ''DELETE'' then
		patient_pk := OLD.fk_patient;
	else
		patient_pk := NEW.fk_patient;
	end if;
	execute ''notify "health_issue_change_db:'' || patient_pk || ''"'';
	return NULL;
end;
';

create trigger tr_h_issues_modified
	after insert or delete or update
	on clin.health_issue
	for each row
		execute procedure audit.trf_announce_h_issue_mod()
;

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-health_issue.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: clin-health_issue.sql,v $
-- Revision 1.2  2006-12-11 17:02:46  ncq
-- - index on modified_by
--
-- Revision 1.1  2006/11/24 09:20:25  ncq
-- - normalize audit trigger/fix col names
--
-- Revision 1.5  2006/10/24 13:09:45  ncq
-- - What it does duplicates the change log so axe it
--
-- Revision 1.4  2006/09/28 14:39:51  ncq
-- - add comment template
--
-- Revision 1.3  2006/09/18 17:32:53  ncq
-- - make more fool-proof
--
-- Revision 1.2  2006/09/16 21:47:37  ncq
-- - improvements
--
-- Revision 1.1  2006/09/16 14:02:36  ncq
-- - use this as a template for change scripts
--
--
