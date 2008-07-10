-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: v9-clin-keyword_expansion-static.sql,v 1.1 2008-07-10 19:49:57 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop table clin.keyword_expansion;
\set ON_ERROR_STOP 1


create table clin.keyword_expansion (
	pk serial primary key,
	fk_staff integer
		references dem.staff(pk),
	keyword text
		not null
		check (trim(keyword) != ''),
	expansion text
		not null,
	unique(fk_staff, keyword)
);

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-clin-keyword_expansion-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v9-clin-keyword_expansion-static.sql,v $
-- Revision 1.1  2008-07-10 19:49:57  ncq
-- - add table for keyword expansion
--
--