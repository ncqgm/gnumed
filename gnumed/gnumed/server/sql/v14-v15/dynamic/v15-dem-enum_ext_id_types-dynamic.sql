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
drop function dem.add_external_id_type(text, text, text) cascade;
\set ON_ERROR_STOP 1

create or replace function dem.add_external_id_type(text, text)
	returns integer
	language 'plpgsql'
	as '
declare
	_name alias for $1;
	_issuer alias for $2;
	_pk int;
begin
	select pk into _pk from dem.enum_ext_id_types where name = _name and issuer = _issuer;
	if FOUND then
		return _pk;
	end if;
	insert into dem.enum_ext_id_types(name, issuer) values (_name, _issuer);
	select currval(pg_get_serial_sequence(''dem.enum_ext_id_types'', ''pk'')) into _pk;
	return _pk;
end;';


comment on function dem.add_external_id_type(text, text) is
	'Add an external ID type if it does not exist yet.
	 This implementation is prone to concurrency issues.';

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view dem.v_external_ids4identity cascade;
\set ON_ERROR_STOP 1

create view dem.v_external_ids4identity as
select
	li2ei.id_identity
		as pk_identity,
	li2ei.id
		as pk_id,
	eit.name
		as name,
	li2ei.external_id
		as value,
	eit.issuer,
	li2ei.comment,
	li2ei.fk_origin
		as pk_type
from
	dem.lnk_identity2ext_id li2ei,
	dem.enum_ext_id_types eit
where
	li2ei.fk_origin = eit.pk
;

grant select on dem.v_external_ids4identity to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v18-dem-enum_ext_id_types-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
