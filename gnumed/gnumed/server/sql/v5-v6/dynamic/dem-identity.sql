-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v5
-- Target database version: v6
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
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

alter table dem.identity drop constraint if exists "identity_title_check";

alter table dem.identity
	add check (trim(coalesce(title, 'NULL')) <> '');


drop function if exists dem.trf_null_empty_title() cascade;

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
