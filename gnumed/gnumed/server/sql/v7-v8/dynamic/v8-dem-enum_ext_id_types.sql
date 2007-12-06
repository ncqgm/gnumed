-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v8-dem-enum_ext_id_types.sql,v 1.2 2007-12-06 08:42:11 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
\set check_function_bodies 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop function dem.add_external_id_type(text, text, text) cascade;
\set ON_ERROR_STOP 1

create or replace function dem.add_external_id_type(text, text, text)
	returns integer
	language 'plpgsql'
	as '
declare
	_name alias for $1;
	_issuer alias for $2;
	_context alias for $3;
	_pk int;
begin
	select pk into _pk from dem.enum_ext_id_types where name = _name and issuer = _issuer;
	if FOUND then
		return _pk;
	end if;
	insert into dem.enum_ext_id_types(name, issuer, context) values (_name, _issuer, _context);
	select currval(pg_get_serial_sequence(''dem.enum_ext_id_types'', ''pk'')) into _pk;
	return _pk;
end;';


comment on function dem.add_external_id_type(text, text, text) is
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
	eit.context,
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
select gm.log_script_insertion('$RCSfile: v8-dem-enum_ext_id_types.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v8-dem-enum_ext_id_types.sql,v $
-- Revision 1.2  2007-12-06 08:42:11  ncq
-- - match detection of existing external ID types to unique index on the table
--
-- Revision 1.1  2007/11/12 22:50:44  ncq
-- - add_external_id() now returns PK
-- - v_external_ids4identity
--
-- Revision 1.1  2007/02/05 13:10:40  ncq
-- - add_external_id_type()
--
-- Revision 1.6  2007/01/27 21:16:08  ncq
-- - the begin/commit does not fit into our change script model
--
-- Revision 1.5  2006/10/24 13:09:45  ncq
-- - What it does duplicates the change log so axe it
--
-- Revision 1.4  2006/09/28 14:39:51  ncq
-- - add comment template
--
-- Revision 1.3  2006/09/18 17:32:53  ncq
-- - make more fool-proof
--
-- Revision 1.2  2006/09/16 21:47:37  ncq
-- - improvements
--
-- Revision 1.1  2006/09/16 14:02:36  ncq
-- - use this as a template for change scripts
--
--
