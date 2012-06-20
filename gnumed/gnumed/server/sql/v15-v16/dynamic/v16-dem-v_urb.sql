-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view dem.v_urb cascade;
\set ON_ERROR_STOP 1



create view dem.v_urb as

select
	u.id as pk_urb,
	u.name as urb,
	u.postcode as postcode_urb,
	u.lat_lon as lat_lon_urb,
	vs.code_state,
	vs.state,
	vs.l10n_state,
	vs.code_country,
	vs.country,
	vs.l10n_country,
	vs.country_deprecated,
	u.id_state as pk_state,
	u.xmin as xmin_urb
from
	dem.urb u
		left join dem.v_state vs on (vs.pk_state = u.id_state)
;



comment on view dem.v_urb is 'denormalizes urb data';



grant select on dem.v_urb to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-dem-v_urb.sql', 'v16');

-- ==============================================================
