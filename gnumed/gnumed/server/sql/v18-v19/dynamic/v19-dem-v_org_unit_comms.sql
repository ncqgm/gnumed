-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- .comment
comment on column dem.lnk_org_unit2comm.comment is 'a comment on this comm channel';


alter table dem.lnk_org_unit2comm
	alter column comment
		set default null;


\unset ON_ERROR_STOP
alter table dem.lnk_org_unit2comm drop constraint dem_lnk_unit2comm_sane_comment;
\set ON_ERROR_STOP 1


alter table dem.lnk_org_unit2comm
	add constraint dem_lnk_unit2comm_sane_comment check (
		gm.is_null_or_non_empty_string(comment) is True
	);

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view dem.v_org_unit_comms cascade;
\set ON_ERROR_STOP 1

create view dem.v_org_unit_comms as
select
	d_lo2c.fk_org_unit
		as pk_org_unit,
	ect.description
		as comm_type,
	_(ect.description)
		as l10n_comm_type,
	d_lo2c.url
		as url,
	d_lo2c.comment
		as comment,
	d_lo2c.is_confidential
		as is_confidential,
	d_lo2c.pk
		as pk_lnk_org_unit2comm,
	d_lo2c.fk_type
		as pk_type,
	d_lo2c.xmin
		as xmin_lnk_org_unit2comm
from
	dem.lnk_org_unit2comm d_lo2c
		inner join dem.enum_comm_types ect on (d_lo2c.fk_type = ect.pk)
;


comment on view dem.v_org_unit_comms is
	'denormalizes org units to communication channels';


grant select on dem.v_org_unit_comms to "gm-doctors", "gm-staff";
grant usage on dem.lnk_org_unit2comm_pk_seq to "gm-doctors", "gm-staff";

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-dem-v_org_unit_comms.sql', '19.0');
