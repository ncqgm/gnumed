-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v8-dem-v_person_names.sql,v 1.1 2007-11-28 11:48:30 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
\set check_function_bodies 1

-- --------------------------------------------------------------
select gm.add_table_for_notifies('dem', 'names', 'name');

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
select gm.log_script_insertion('$RCSfile: v8-dem-v_person_names.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v8-dem-v_person_names.sql,v $
-- Revision 1.1  2007-11-28 11:48:30  ncq
-- - new view
--
--