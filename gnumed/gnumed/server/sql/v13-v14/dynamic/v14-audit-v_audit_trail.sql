-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

set default_transaction_read_only to off;

-- --------------------------------------------------------------
create or replace view audit.v_audit_trail as

	-- all audit log tables are children of audit.audit_trail
	select
		to_char(aat.audit_when, 'YYYY-MM-DD HH24:MI')
			as event_when,
		coalesce (
			(select short_alias from dem.staff where db_user = aat.audit_by),
			'<' || aat.audit_by || '>'
		)
			as event_by,
		aat.orig_tableoid::regclass
			as event_table,
		aat.orig_version
			as row_version_before,
		case
			when aat.audit_action = 'DELETE' then NULL::integer
			else (aat.orig_version + 1)
		end
			as row_version_after,
		aat.audit_action
			as event,
		aat.audit_when
			as audit_when_ts,
		aat.pk_audit
			as pk_audit
	from
		audit.audit_trail aat


union all


	select
		to_char(gal.modified_when, 'YYYY-MM-DD HH24:MI')
			as event_when,
		coalesce (
			(select short_alias from dem.staff where db_user = gal.modified_by),
			'<' || gal.modified_by || '>'
		)
			as event_by,
		'gm.access_log'::regclass
			as event_table,
		NULL::integer
			as row_version_before,
		'0'::integer
			as row_version_after,
		gal.user_action
			as event,
		gal.modified_when
			as audit_when_ts,
		gal.pk_audit
			as pk_audit
	from
		gm.access_log gal
	where
		gal.row_version = 0


union all

	-- all original data tables are children of audit.audit_fields
	select
		to_char(aaf.modified_when, 'YYYY-MM-DD HH24:MI')
			as event_when,
		coalesce (
			(select short_alias from dem.staff where db_user = aaf.modified_by),
			'<' || aaf.modified_by || '>'
		)
			as event_by,
		aaf.tableoid::regclass
			as event_table,
		NULL::integer
			as row_version_before,
		'0'::integer
			as row_version_after,
		'INSERT'::text
			as event,
		aaf.modified_when
			as audit_when_ts,
		aaf.pk_audit
			as pk_audit
	from
		audit.audit_fields aaf
	where
		aaf.row_version = 0
;


grant select on audit.v_audit_trail to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v14-clin-clin_narrative-dynamic.sql', 'Revision: 1.1');
