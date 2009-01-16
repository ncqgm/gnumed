-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v10-clin-waiting_list-dynamic.sql,v 1.1 2009-01-16 13:30:40 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.waiting_list
	add constraint non_empty_area
		check (trim(area) <> '');


\unset ON_ERROR_STOP
drop view clin.v_waiting_list cascade;
\set ON_ERROR_STOP 1

create view clin.v_waiting_list as
select
	wl.list_position
		as list_position,
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
	vmre.started
		as start_most_recent_encounter,
	vmre.reason_for_encounter
		as most_recent_rfe,
	wl.comment
		as comment,
	(select started from clin.encounter ce
	 where vmre.pk_encounter = ce.pk
	 order by last_affirmed desc limit 1 offset 1
	)	as start_previous_encounter,
	i.pk
		as pk_identity,
	n.id
		as pk_name,
	i.pupic
		as pupic
from
	clin.waiting_list wl,
	dem.identity i,
	dem.names n,
	clin.v_most_recent_encounters vmre
where
	wl.fk_patient = i.pk and
	wl.fk_patient = n.id_identity and
	wl.fk_patient = vmre.pk_patient and
	i.deceased is NULL and
	n.active is true
;


insert into clin.waiting_list (
	fk_patient,
	list_position,
	comment,
	area
) values (
	12,
	1,
	'wants to see Dr.McCoy for scar problems',
	'LMcC'
);

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-clin-waiting_list-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-clin-waiting_list-dynamic.sql,v $
-- Revision 1.1  2009-01-16 13:30:40  ncq
-- - new
--
--