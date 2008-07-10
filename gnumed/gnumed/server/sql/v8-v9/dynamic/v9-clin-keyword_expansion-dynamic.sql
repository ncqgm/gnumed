-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: v9-clin-keyword_expansion-dynamic.sql,v 1.1 2008-07-10 19:50:40 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on table clin.keyword_expansion is
'A table for expanding text typed by the user based on keywords.';

comment on column clin.keyword_expansion.fk_staff is
'The provider this expansion applies to.
If NULL: applies to all providers.';

comment on column clin.keyword_expansion.keyword is
'The keyword to expand. Can only exist once per provider.';

comment on column clin.keyword_expansion.expansion is
'The expansion for this keyword.';

-- --------------------------------------------------------------
grant select, insert, update, delete on
	clin.keyword_expansion
	, clin.keyword_expansion_pk_seq
to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-clin-keyword_expansion-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v9-clin-keyword_expansion-dynamic.sql,v $
-- Revision 1.1  2008-07-10 19:50:40  ncq
-- - add table for keyword expansion
--
--