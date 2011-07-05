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
drop view dem.v_street cascade;
\set ON_ERROR_STOP 1



create view dem.v_street as

select
	st.id as pk_street,
	st.name as street,
	coalesce(st.postcode, vu.postcode_urb) as postcode,
	st.postcode as postcode_street,
	st.lat_lon as lat_lon_street,
	st.suburb as suburb,
	vu.urb,
	vu.postcode_urb,
	vu.lat_lon_urb,
	vu.code_state,
	vu.state,
	vu.l10n_state,
	vu.code_country,
	vu.country,
	vu.l10n_country,
	vu.country_deprecated,
	st.id_urb as pk_urb,
	vu.pk_state,
	st.xmin as xmin_street
from
	dem.street st
		left join dem.v_urb vu on (st.id_urb = vu.pk_urb)
;



comment on view dem.v_street is 'denormalizes street data';



grant select on dem.v_street to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-dem-v_street.sql', 'v16');

-- ==============================================================
