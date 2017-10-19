-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_waiting_list cascade;
\set ON_ERROR_STOP 1

create view clin.v_waiting_list as
select
	wl.list_position
		as list_position,
	wl.area
		as waiting_zone,
	wl.urgency
		as urgency,
	i.title
		as title,
	n.firstnames
		as firstnames,
	n.lastnames
		as lastnames,
	n.preferred
		as preferred_name,
	i.dob
		as dob,
	i.gender
		as gender,
	_(i.gender)
		as l10n_gender,
	wl.registered
		as registered,
	(select now() - wl.registered)
		as waiting_time,
	(select to_char(age(now(), wl.registered), 'DDD HH24:MI'))
		as waiting_time_formatted,
	wl.comment
		as comment,
	i.pk
		as pk_identity,
	n.id
		as pk_name,
	i.pupic
		as pupic,
	wl.pk
		as pk_waiting_list
from
	clin.waiting_list wl,
	dem.identity i,
	dem.names n
where
	wl.fk_patient = i.pk and
	wl.fk_patient = n.id_identity and
	i.deceased is NULL and
	n.active is true
;


grant select on clin.v_waiting_list to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-v_waiting_list-fixup.sql', '17.1 (=16.17)');
