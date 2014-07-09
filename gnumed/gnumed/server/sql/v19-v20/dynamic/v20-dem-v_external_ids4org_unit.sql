-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop view if exists dem.v_external_ids4org_unit cascade;

create view dem.v_external_ids4org_unit as
select
	d_lou2ei.fk_org_unit
		as pk_org_unit,
	d_lou2ei.pk
		as pk_id,
	d_eit.name
		as name,
	d_lou2ei.external_id
		as value,
	d_eit.issuer,
	d_lou2ei.comment,
	d_lou2ei.fk_type
		as pk_type
from
	dem.lnk_org_unit2ext_id d_lou2ei
		join dem.enum_ext_id_types d_eit on d_lou2ei.fk_type = d_eit.pk
;

grant select on dem.v_external_ids4org_unit to group "gm-staff";
grant usage on dem.lnk_org_unit2ext_id_pk_seq to group "gm-staff";

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-dem-v_external_ids4org_unit.sql', '20.0');
