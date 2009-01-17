-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v10-clin-waiting_list-dynamic.sql,v 1.2 2009-01-17 23:16:35 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
alter table clin.waiting_list drop constraint non_empty_area;
\set ON_ERROR_STOP 1

alter table clin.waiting_list
	add constraint non_empty_area
		check (trim(area) <> '');

comment on column clin.waiting_list.area is
	'an arbitrary value by which filtering waiting patients into zones becomes possible';

select gm.add_table_for_notifies('clin', 'waiting_list');
select gm.add_table_for_notifies('clin', 'waiting_list', 'waiting_list_generic');


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
	(select to_char(age(now(), wl.registered), 'HH24:MI'))
		as waiting_time_formatted,
--	(select started from clin.v_most_recent_encounters where wl.fk_patient = vmre.pk_patient)
--		as start_most_recent_encounter,
--	(select reason_for_encounter from clin.v_most_recent_encounters where wl.fk_patient = vmre.pk_patient)
--		as most_recent_rfe,
	wl.comment
		as comment,
--	(select started from clin.encounter ce
--	 where vmre.pk_encounter = ce.pk
--	 order by last_affirmed desc limit 1 offset 1
--	)	as start_previous_encounter,
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
select gm.log_script_insertion('$RCSfile: v10-clin-waiting_list-dynamic.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v10-clin-waiting_list-dynamic.sql,v $
-- Revision 1.2  2009-01-17 23:16:35  ncq
-- - add proper signals
-- - improve view
--
-- Revision 1.1  2009/01/16 13:30:40  ncq
-- - new
--
--