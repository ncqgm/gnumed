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
drop view if exists dem.v_person_names cascade;


create view dem.v_person_names as

select
	d_i.pk
		as pk_identity,
	d_n.active
		as active_name,
	d_i.title,
	d_n.firstnames,
	d_n.lastnames,
	d_n.preferred,
	d_n.comment,
	d_i.comment
		as comment_identity,
	d_i.gender,
	d_i.dob,
	d_i.tob,
	d_i.deceased
		as dod,
	d_i.deleted
		as identity_deleted,
	(d_i.deceased is not null)
		as deceased,
	d_n.id
		as pk_name,
	d_n.xmin
		as xmin_name
from
	dem.names d_n
		join dem.identity d_i on (d_n.id_identity = d_i.pk)
where
	d_i.pk = d_n.id_identity
;

grant select on dem.v_person_names to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-dem-v_person_names.sql', '22.0');
