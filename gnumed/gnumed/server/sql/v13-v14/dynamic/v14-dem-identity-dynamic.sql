-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- .emergency_contact
\unset ON_ERROR_STOP
alter table dem.identity drop constraint sane_emergency_contact cascade;
\set ON_ERROR_STOP 1


alter table dem.identity
	add constraint sane_emergency_contact
		check (gm.is_null_or_non_empty_string(emergency_contact) is True);



-- .fk_emergency_contact
alter table dem.identity
	add foreign key (fk_emergency_contact) references dem.identity(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
select gm.log_script_insertion('v14-dem-identity-dynamic.sql', 'Revision: 1.1');
