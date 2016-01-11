-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
set check_function_bodies to on;
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- audit.audit_fields
-- actually, there's an INSERT trigger on child tables already
-- which forces .modified_when to now()
alter table audit.audit_fields
	drop constraint if exists
		audit_audit_fields_sane_modified_when cascade;

alter table audit.audit_fields
	add constraint audit_audit_fields_sane_modified_when check
		((modified_when <= clock_timestamp()) IS TRUE)
;


-- add a foreign key which is, however, NOT ENFORCED
-- this should cue in pg_dump about the needed order
-- of dumping dem.staff vs other tables ...
--
-- actually, this needs to be put into all child tables
-- and link against dem.staff.db_user (but not be enforced)
--
--alter table audit.audit_fields
--	drop constraint if exists fk_audit_audit_fields_dem_staff_db_user cascade
--;
--
--alter table audit.audit_fields
--	add constraint fk_audit_audit_fields_dem_staff_db_user
--		foreign key (modified_by)
--		references dem.staff(db_user)
--		on update restrict
--		on delete restrict
--		not valid
--;


create or replace function gm.account_is_dbowner_or_staff(_account name)
	returns boolean
	language plpgsql
	as '
DECLARE
	_is_owner boolean;
BEGIN
	-- is _account member of current db group ?
--	PERFORM 1 FROM pg_auth_members
--	WHERE
--		roleid = (SELECT oid FROM pg_roles WHERE rolname = current_database())
--			AND
--		member = (SELECT oid FROM pg_roles WHERE rolname = _account)
--	;
--	IF FOUND THEN
--		-- should catch people on staff, gm-dbo, and postgres
--		RETURN TRUE;
--	END IF;

	-- postgres
	IF _account = ''postgres'' THEN
		RETURN TRUE;
	END IF;

	-- on staff list
	PERFORM 1 FROM dem.staff WHERE db_user = _account;
	IF FOUND THEN
		RETURN TRUE;
	END IF;

	-- owner
	SELECT pg_catalog.pg_get_userbyid(datdba) = _account INTO STRICT _is_owner FROM pg_catalog.pg_database WHERE datname = current_database();
	IF _is_owner IS TRUE THEN
		RETURN TRUE;
	END IF;

	RETURN FALSE;
END;';

-- --------------------------------------------------------------
-- audit.audit_trail
alter table audit.audit_trail
	drop constraint if exists
		audit_audit_trail_sane_orig_when cascade;

alter table audit.audit_trail
	add constraint audit_audit_trail_sane_orig_when check
		((orig_when <= clock_timestamp()) IS TRUE)
;


alter table audit.audit_trail
	drop constraint if exists
		audit_audit_trail_sane_audit_when cascade;

alter table audit.audit_trail
	add constraint audit_audit_trail_sane_audit_when check
		((audit_when <= clock_timestamp()) IS TRUE)
;

alter table audit.audit_trail
	drop constraint if exists
		audit_audit_trail_orig_before_audit_when cascade;

alter table audit.audit_trail
	add constraint audit_audit_trail_orig_before_audit_when check
		((orig_when <= audit_when) IS TRUE)
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-audit-audit_constraints.sql', '21.0');
