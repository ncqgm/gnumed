-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-dem-v_person_comms.sql,v 1.2 2008-01-07 20:31:14 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
\set check_function_bodies 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view dem.v_person_comms cascade;
\set ON_ERROR_STOP 1

create view dem.v_person_comms as
select
	li2c.fk_identity as pk_identity,
	ect.description as comm_type,
	_(ect.description) as l10n_comm_type,
	li2c.url as url,
	li2c.is_confidential as is_confidential,
	li2c.pk as pk_lnk_identity2comm,
	li2c.fk_address as pk_address,
	li2c.fk_type as pk_type,
	li2c.xmin as xmin_lnk_identity2comm
from
	dem.lnk_identity2comm li2c,
	dem.enum_comm_types ect
where
	li2c.fk_type = ect.pk
;

comment on view dem.v_person_comms is
	'denormalizes persons to communications channels';

grant select on dem.v_person_comms to group "gm-doctors";


select gm.add_table_for_notifies('dem'::name, 'lnk_identity2comm'::name, 'comm_channel'::name);

-- --------------------------------------------------------------
create or replace function dem.create_comm_type(text)
	returns integer
	language plpgsql
	as E'
DECLARE
	_description alias for $1;
	_pk_type integer;
BEGIN
	select pk into _pk_type from dem.enum_comm_types where _(description) = _description;
	if FOUND then
		return _pk_type;
	end if;

	select pk into _pk_type from dem.enum_comm_types where description = _description;
	if FOUND then
		return _pk_type;
	end if;

	insert into dem.enum_comm_types(description) values (_description);
	select currval(pg_get_serial_sequence(''dem.enum_comm_types'', ''pk'')) into _pk_type;
	return _pk_type;
END;';

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-dem-v_person_comms.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v9-dem-v_person_comms.sql,v $
-- Revision 1.2  2008-01-07 20:31:14  ncq
-- - normalize view column names
-- - add table for audit
-- - dem.create_comm_type()
--
-- Revision 1.1  2008/01/07 14:57:38  ncq
-- - adjust to column name changes
-- - include XMIN
--
--
