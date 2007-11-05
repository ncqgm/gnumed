-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v7
-- Target database version: v8
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: clin-adjust_soap_cat.sql,v 1.1 2007-11-05 11:35:56 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- clin.clin_root_item
\unset ON_ERROR_STOP
alter table clin.clin_root_item
	alter column soap_cat
		drop not null;
alter table clin.clin_root_item
	drop constraint clin_root_item_soap_cat_check;
\set ON_ERROR_STOP 1

alter table clin.clin_root_item
	add check
		((soap_cat is NULL) or (lower(soap_cat) in ('s', 'o', 'a', 'p')));

comment on column clin.clin_root_item.soap_cat is
	'each clinical item must be either one of the S, O, A, P
	 categories or NULL to indicate a non-clinical item';


-- clin.soap_cat_ranks
\unset ON_ERROR_STOP
alter table clin.soap_cat_ranks
	alter column soap_cat
		drop not null;
alter table clin.soap_cat_ranks
	drop constraint soap_cat_ranks_soap_cat_check;
alter table clin.soap_cat_ranks
	drop constraint soap_cat_ranks_rank_check;
\set ON_ERROR_STOP 1

alter table clin.soap_cat_ranks
	add check
		((soap_cat is NULL) or (lower(soap_cat) in ('s', 'o', 'a', 'p')));

alter table clin.soap_cat_ranks
	add check
		(rank in (1,2,3,4,5));

delete from clin.soap_cat_ranks where soap_cat is NULL;
insert into clin.soap_cat_ranks (soap_cat, rank) values (NULL, 5);


-- clin.clin_narrative
\unset ON_ERROR_STOP
drop index clin.idx_narr_soap cascade;
\set ON_ERROR_STOP 1

create index idx_narr_soap on clin.clin_narrative(soap_cat) where (lower(soap_cat) in ('s', 'o', 'a', 'p'));

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: clin-adjust_soap_cat.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: clin-adjust_soap_cat.sql,v $
-- Revision 1.1  2007-11-05 11:35:56  ncq
-- - new
--
-- Revision 1.7  2007/05/07 16:32:09  ncq
-- - log_script_insertion() now in gm.
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
