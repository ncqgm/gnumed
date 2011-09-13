-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- .dob
update dem.identity set
	dob = null,
	comment = coalesce(comment || '; ', '') || 'DOB-in-future (' || to_char(dob, 'Dy, YYYY-MM-DD, HH24:MI:SS.MS') || ') set to NULL'
where
	dob > now()
;


\unset ON_ERROR_STOP
alter table dem.identity drop constraint dem_identity_sane_dob cascade;
\set ON_ERROR_STOP 1

alter table dem.identity
	add constraint dem_identity_sane_dob
		check (
			(dob is NULL)
				or
			(dob <= now())
		);

-- --------------------------------------------------------------
-- .dod
\unset ON_ERROR_STOP
alter table dem.identity drop constraint identity_check cascade;
alter table dem.identity drop constraint dem_identity_sane_dod cascade;
\set ON_ERROR_STOP 1

alter table dem.identity
	add constraint dem_identity_sane_dod
		check (
			(deceased is NULL)
				or
			(dob is NULL)
				or
			(deceased >= dob)
		);

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-dem-identity-dynamic.sql', 'v16');

-- ==============================================================
