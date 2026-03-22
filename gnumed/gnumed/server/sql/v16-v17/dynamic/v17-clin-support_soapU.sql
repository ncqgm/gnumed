-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- clin.clin_root_item
alter table clin.clin_root_item	drop constraint if exists clin_root_item_soap_cat_check;
alter table clin.clin_root_item	drop constraint if exists clin_root_item_sane_soap_cat;
alter table clin.clin_root_item	drop constraint if exists clin_root_item_soap_cat;

alter table clin.clin_root_item
	add constraint clin_root_item_sane_soap_cat check
		((soap_cat is NULL) or (lower(soap_cat) in ('s', 'o', 'a', 'p', 'u')));

comment on column clin.clin_root_item.soap_cat is
	'each clinical item must be either one of the S, O, A, P, U
	 categories or NULL to indicate a non-clinical item, U meaning Unspecified-but-clinical';


-- clin.soap_cat_ranks
alter table clin.soap_cat_ranks	drop constraint if exists soap_cat_ranks_soap_cat_check;
alter table clin.soap_cat_ranks	drop constraint if exists clin_soap_cat_ranks_sane_cats;
alter table clin.soap_cat_ranks	drop constraint if exists soap_cat_ranks_rank_check;
alter table clin.soap_cat_ranks	drop constraint if exists clin_soap_cat_ranks_sane_ranks;

alter table clin.soap_cat_ranks
	add constraint clin_soap_cat_ranks_sane_cats check
		((soap_cat is NULL) or (lower(soap_cat) in ('s', 'o', 'a', 'p', 'u')));

alter table clin.soap_cat_ranks
	add constraint clin_soap_cat_ranks_sane_ranks check
		(rank in (1,2,3,4,5,6));

delete from clin.soap_cat_ranks where soap_cat = 'u';
insert into clin.soap_cat_ranks (soap_cat, rank) values ('u', 5);

delete from clin.soap_cat_ranks where soap_cat is NULL;
insert into clin.soap_cat_ranks (soap_cat, rank) values (NULL, 6);


-- clin.clin_narrative
drop index if exists clin.idx_narr_soap cascade;
drop index if exists clin.idx_narrative_soap_cat cascade;

create index idx_narrative_soap_cat on clin.clin_narrative(soap_cat) where (lower(soap_cat) in ('s', 'o', 'a', 'p', 'u'));

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-clin-support_soapU.sql', '17.0');
