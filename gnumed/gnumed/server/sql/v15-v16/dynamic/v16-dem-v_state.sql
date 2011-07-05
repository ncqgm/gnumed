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
drop view dem.v_state cascade;
\set ON_ERROR_STOP 1



create view dem.v_state as

select
	s.id as pk_state,
	s.code as code_state,
	s.name as state,
	_(s.name) as l10n_state,
	s.country as code_country,
	c.name as country,
	_(c.name) as l10n_country,
	c.deprecated as country_deprecated,
	s.xmin as xmin_state
from
	dem.state as s
		left join dem.country c on (s.country = c.code)
;



comment on view dem.v_state is 'denormalizes state information';



grant select on dem.v_state to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-dem-v_state.sql', 'v16');

-- ==============================================================
