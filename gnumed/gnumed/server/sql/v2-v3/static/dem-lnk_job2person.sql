-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: dem-lnk_job2person.sql,v 1.1 2006-11-19 10:17:03 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- drop foreign keys
\unset ON_ERROR_STOP
alter table dem.lnk_job2person
	drop constraint "$1";
alter table dem.lnk_job2person
	drop constraint "lnk_job2person_id_identity_fkey";

alter table dem.lnk_job2person
	drop constraint "$2";
alter table dem.lnk_job2person
	drop constraint "lnk_job2person_id_occupation_fkey";
\set ON_ERROR_STOP 1

-- rename columns
alter table dem.lnk_job2person
	rename column id to pk;

alter table dem.lnk_job2person
	rename column id_identity to fk_identity;

alter table dem.lnk_job2person
	rename column id_occupation to fk_occupation;

alter table dem.lnk_job2person
	rename column comment to activities;

-- readd foreign keys
alter table dem.lnk_job2person
	add foreign key(fk_identity)
		references dem.identity(pk)
		on update cascade
		on delete cascade;

alter table dem.lnk_job2person
	add foreign key(fk_occupation)
		references dem.occupation(id)
		on update cascade
		on delete restrict;

-- comment
comment on column dem.lnk_job2person.activities is
	'describes activities the person is usually
	 carrying out when working at this job';

-- --------------------------------------------------------------
-- don't forget appropriate grants
grant select, insert, update, delete on dem.lnk_job2person to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: dem-lnk_job2person.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: dem-lnk_job2person.sql,v $
-- Revision 1.1  2006-11-19 10:17:03  ncq
-- - rename columns to better reflect usage
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
