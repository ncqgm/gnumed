-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- audit.audit_fields
-- actually, there's an INSERT trigger on child tables already
alter table audit.audit_fields
	drop constraint if exists
		audit_audit_fields_sane_modified_when cascade;

alter table audit.audit_fields
	add constraint audit_audit_fields_sane_modified_when check
		((modified_when <= clock_timestamp()) IS TRUE)
;

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
