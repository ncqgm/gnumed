-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten.Hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

set check_function_bodies to on;
-- --------------------------------------------------------------
drop function if exists dem.trf_prevent_deletion_of_in_use_staff() cascade;

create or replace function dem.trf_prevent_deletion_of_in_use_staff()
	returns trigger
	 language 'plpgsql'
	as '
BEGIN
	-- does any audited table contain the dem.staff.db_user we are about to delete ?
	PERFORM 1 FROM audit.audit_fields WHERE modified_by = OLD.db_user LIMIT 1;
	IF FOUND THEN
		RAISE EXCEPTION
			''DELETE from dem.staff: Sanity check failed. User <%> is referenced from <.modified_by> of at least one audited table.'', OLD.db_user
			USING ERRCODE = ''foreign_key_violation''
		;
		RETURN NULL;
	END IF;

	-- does any audit table contain the dem.staff.db_user we are about to delete ?
	PERFORM 1 FROM audit.audit_trail WHERE orig_by = OLD.db_user OR audit_by = OLD.db_user LIMIT 1;
	IF FOUND THEN
		RAISE EXCEPTION
			''DELETE from dem.staff: Sanity check failed. User <%> is referenced from <.orig_by> or <.audit_by> of at least one audit table.'', OLD.db_user
			USING ERRCODE = ''foreign_key_violation''
		;
		RETURN NULL;
	END IF;

	RETURN OLD;
END;
';

comment on function dem.trf_prevent_deletion_of_in_use_staff() is
	'this function is used to prevent DELETEs of staff members which had been used to store data';


drop trigger if exists tr_prevent_deletion_of_in_use_staff on dem.staff cascade;

create trigger tr_prevent_deletion_of_in_use_staff
	before delete on dem.staff
	for each row execute procedure dem.trf_prevent_deletion_of_in_use_staff();

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-dem-staff-dynamic.sql', '21.0');
