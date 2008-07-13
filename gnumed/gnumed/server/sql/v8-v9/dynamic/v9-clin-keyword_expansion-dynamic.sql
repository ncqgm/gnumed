-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: v9-clin-keyword_expansion-dynamic.sql,v 1.2 2008-07-13 16:24:38 ncq Exp $
-- $Revision: 1.2 $

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

comment on column clin.keyword_expansion.owner is
'Who "owns" this text expansion.';


grant select, insert, update, delete on
	clin.keyword_expansion
	, clin.keyword_expansion_pk_seq
to group "gm-doctors";

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_keyword_expansions cascade;
\set ON_ERROR_STOP 1

create view clin.v_keyword_expansions as
select
	cke.pk
		as pk_keyword_expansion,
	cke.fk_staff
		as pk_staff,
	cke.keyword
		as keyword,
	cke.expansion
		as expansion,
	(cke.fk_staff is null)
		as public_expansion,
	(cke.fk_staff is not null)
		as private_expansion,
	cke.owner
		as owner
from
	clin.keyword_expansion cke
;


grant select on
	clin.v_keyword_expansions
to group "gm-doctors";

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_your_keyword_expansions cascade;
\set ON_ERROR_STOP 1

create view clin.v_your_keyword_expansions as
select distinct on (keyword) *
from (
	select
		cke.pk
			as pk_keyword_expansion,
		cke.fk_staff
			as pk_staff,
		cke.keyword
			as keyword,
		cke.expansion
			as expansion,
		false
			as public_expansion,
		true
			as private_expansion,
		cke.owner
			as owner
	from clin.keyword_expansion cke
	where fk_staff = (select pk from dem.staff where db_user = current_user)

		union all

	select
		cke.pk
			as pk_keyword_expansion,
		cke.fk_staff
			as pk_staff,
		cke.keyword
			as keyword,
		cke.expansion
			as expansion,
		true
			as public_expansion,
		false
			as private_expansion,
		cke.owner
			as owner
	from
		clin.keyword_expansion cke
	where
		fk_staff is null
	order by
		private_expansion desc
	) as union_result
;


grant select on
	clin.v_your_keyword_expansions
to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-clin-keyword_expansion-dynamic.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v9-clin-keyword_expansion-dynamic.sql,v $
-- Revision 1.2  2008-07-13 16:24:38  ncq
-- - comment on owner
-- - clin.v_keyword_expansions
-- - clin.v_your_keyword_expansions
--
-- Revision 1.1  2008/07/10 19:50:40  ncq
-- - add table for keyword expansion
--
--