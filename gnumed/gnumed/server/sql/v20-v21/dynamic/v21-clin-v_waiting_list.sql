-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1

--set default_transaction_read_only to off;

-- --------------------------------------------------------------
drop view if exists clin.v_waiting_list cascade;

create view clin.v_waiting_list as
select
	c_wl.list_position
		as list_position,
	c_wl.area
		as waiting_zone,
	c_wl.urgency
		as urgency,
	d_i.title
		as title,
	d_n.firstnames
		as firstnames,
	d_n.lastnames
		as lastnames,
	d_n.preferred
		as preferred_name,
	d_i.dob
		as dob,
	d_i.gender
		as gender,
	_(d_i.gender)
		as l10n_gender,
	d_i.comment
		as comment_identity,
	c_wl.registered
		as registered,
	(select now() - c_wl.registered)
		as waiting_time,
	(select to_char(age(now(), c_wl.registered), 'DDD HH24:MI'))
		as waiting_time_formatted,
	c_wl.comment
		as comment,
	d_i.pk
		as pk_identity,
	d_n.id
		as pk_name,
	c_wl.pk
		as pk_waiting_list
from
	clin.waiting_list c_wl,
	dem.identity d_i,
	dem.names d_n
where
	c_wl.fk_patient = d_i.pk
		and
	c_wl.fk_patient = d_n.id_identity
		and
	d_i.deceased is NULL
		and
	d_n.active is TRUE
;


revoke all on clin.v_waiting_list from public;
grant select on clin.v_waiting_list to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-clin-v_waiting_list.sql', '21.0');
