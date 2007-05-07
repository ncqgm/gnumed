-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v5
-- Target database version: v6
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: dem-identity.sql,v 1.3 2007-05-07 16:33:06 ncq Exp $
-- $Revision: 1.3 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- adjust dem.identity.title
alter table dem.identity
	alter column title
		set default null;


update dem.identity
	set title = NULL
	where
		title is not NULL and
		trim(title) = '';

\unset ON_ERROR_STOP
alter table dem.identity drop constraint "identity_title_check";
\set ON_ERROR_STOP 1

alter table dem.identity
	add check (trim(coalesce(title, 'NULL')) <> '');


\unset ON_ERROR_STOP
drop function dem.trf_null_empty_title() cascade;
\set ON_ERROR_STOP 1

create function dem.trf_null_empty_title()
	returns trigger
	language plpgsql
	as '
begin
	if (NEW.title is null) then
		return NEW;
	end if;

	if trim(NEW.title) <> '''' then
		return NEW;
	end if;

	NEW.title := NULL;
	return NEW;
end;';


create trigger tr_null_empty_title
	before insert or update on dem.identity
	for each row execute procedure dem.trf_null_empty_title()
;


-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: dem-identity.sql,v $', '$Revision: 1.3 $');

-- ==============================================================
-- $Log: dem-identity.sql,v $
-- Revision 1.3  2007-05-07 16:33:06  ncq
-- - log_script_insertion() now in gm.
--
-- Revision 1.2  2007/04/21 19:43:39  ncq
-- - properly check title for empty string
--
-- Revision 1.1  2007/04/20 08:18:03  ncq
-- - tighten dem.identity.title handling
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
