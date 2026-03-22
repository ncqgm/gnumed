-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop index if exists clin.idx_health_issue_modified_by;

create index idx_health_issue_modified_by on clin.health_issue(modified_by);

-- --------------------------------------------------------------
drop function if exists clin.f_announce_h_issue_mod() cascade;
drop function if exists audit.trf_announce_h_issue_mod() cascade;

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
