-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1
\set check_function_bodies 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view dem.v_org_unit_comms cascade;
\set ON_ERROR_STOP 1

create view dem.v_org_unit_comms as
select
	lo2c.fk_org_unit as pk_org_unit,
	ect.description as comm_type,
	_(ect.description) as l10n_comm_type,
	lo2c.url as url,
	lo2c.is_confidential as is_confidential,
	lo2c.pk as pk_lnk_org_unit2comm,
--	lo2c.fk_address as pk_address,
	lo2c.fk_type as pk_type,
	lo2c.xmin as xmin_lnk_org_unit2comm
from
	dem.lnk_org_unit2comm lo2c
		inner join dem.enum_comm_types ect on (lo2c.fk_type = ect.pk)
;

comment on view dem.v_org_unit_comms is
	'denormalizes org units to communication channels';

grant select on dem.v_org_unit_comms to "gm-doctors", "gm-staff";
grant usage on dem.lnk_org_unit2comm_pk_seq to "gm-doctors", "gm-staff";


select gm.add_table_for_notifies('dem'::name, 'lnk_org_unit2comm'::name, 'org_unit_comm_channel'::name);

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-dem-v_org_unit_comms.sql', 'v16');

-- ==============================================================
