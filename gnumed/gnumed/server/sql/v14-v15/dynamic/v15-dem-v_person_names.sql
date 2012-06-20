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
drop view dem.v_person_names cascade;
\set ON_ERROR_STOP 1

create view dem.v_person_names as

select
	dn.id_identity
		as pk_identity,
	dn.active
		as active_name,
	di.title,
	dn.firstnames,
	dn.lastnames,
	dn.preferred,
	dn.comment,
	di.gender,
	di.dob,
	di.tob,
	di.deceased
		as dod,
	di.deleted
		as identity_deleted,
	(di.deceased is not null)
		as deceased,
	dn.id
		as pk_name,
	dn.xmin
		as xmin_name
from
	dem.names dn,
	dem.identity di
where
	di.pk = dn.id_identity
;

grant select on dem.v_person_names to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-dem-v_person_names.sql', '1.3');

-- ==============================================================
