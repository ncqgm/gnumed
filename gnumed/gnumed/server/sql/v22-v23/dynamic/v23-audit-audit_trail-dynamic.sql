-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
DO '
	BEGIN
		alter table audit.audit_trail rename column pk_audit to pk_audit_trail;
    EXCEPTION
        WHEN undefined_column THEN RAISE NOTICE ''audit.audit_trail.pk_audit does not exist'';
	END
';
comment on column audit.audit_trail.pk_audit_trail is '
the primary key for this log entry,
not related to the primary key of the logged row,
unique within the audit logging system';


DO '
	BEGIN
		alter table audit.audit_trail rename column orig_tableoid to src_table_oid;
    EXCEPTION
        WHEN undefined_column THEN RAISE NOTICE ''audit.audit_trail.orig_tableoid does not exist'';
	END
';
comment on column audit.audit_trail.src_table_oid is
	'the OID of the table this log entry comes from (TG_RELID when the audit trigger ran)';


DO '
	BEGIN
		alter table audit.audit_trail rename column orig_version to row_version;
    EXCEPTION
        WHEN undefined_column THEN RAISE NOTICE ''audit.audit_trail.orig_version does not exist'';
	END
';
comment on column audit.audit_trail.row_version is
	'value of .row_version of the row in the table this log entry comes from,
IOW, which row version was turned into this log entry';


DO '
	BEGIN
		alter table audit.audit_trail rename column orig_by to version_created_by;
    EXCEPTION
        WHEN undefined_column THEN RAISE NOTICE ''audit.audit_trail.orig_by does not exist'';
	END
';
comment on column audit.audit_trail.version_created_by is
	'value of .modified_by of the row in the table this log entry comes from,
IOW, who created the row version that this log entry represents,';


DO '
	BEGIN
		alter table audit.audit_trail rename column orig_when to version_created_when;
    EXCEPTION
        WHEN undefined_column THEN RAISE NOTICE ''audit.audit_trail.orig_when does not exist'';
	END
';
comment on column audit.audit_trail.version_created_when is
	'value of .modified_when of the row in the table this log entry comes from,
IOW, the creation timestamp of the row version this log entry represents,
(not of this log record itself, for that see .log_created_when)';


DO '
	BEGIN
		alter table audit.audit_trail rename column audit_action to log_reason;
    EXCEPTION
        WHEN undefined_column THEN RAISE NOTICE ''audit.audit_trail.audit_action does not exist'';
	END
';
comment on column audit.audit_trail.log_reason is
	'Why was this log entry created (UPDATE or DELETE to the original row).';


DO '
	BEGIN
		alter table audit.audit_trail rename column audit_by to log_created_by;
    EXCEPTION
        WHEN undefined_column THEN RAISE NOTICE ''audit.audit_trail.audit_by does not exist'';
	END
';
comment on column audit.audit_trail.log_created_by is
	'Who created this log entry.
Should be equal to .modified_by of the *next* version of the logged row.';


DO '
	BEGIN
		alter table audit.audit_trail rename column audit_when to log_created_when;
    EXCEPTION
        WHEN undefined_column THEN RAISE NOTICE ''audit.audit_trail.audit_when does not exist'';
	END
';
comment on column audit.audit_trail.log_created_when is
	'When was this log entry created (not when the logged row was created).';


alter table audit.audit_trail add column if not exists src_row_pk_audit integer;
comment on column audit.audit_trail.src_row_pk_audit is
	'Value of .pk_audit of row in table this log entry came from,
uniquely identifies this row, regardless of version';

alter table audit.audit_trail
	drop constraint if exists audit__audit_trail__uniq_row_version_per_row;

alter table audit.audit_trail
	add constraint audit__audit_trail__uniq_row_ver_per_row
		unique (src_row_pk_audit, row_version);

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-audit-audit_trail-dynamic.sql', 'v23');
