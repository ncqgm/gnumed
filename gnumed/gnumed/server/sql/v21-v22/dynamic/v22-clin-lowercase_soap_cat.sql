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
alter table clin.clin_root_item	drop constraint if exists clin_root_item_sane_soap_cat;

alter table clin.clin_root_item
	add constraint clin_root_item_sane_soap_cat check
		((soap_cat is NULL) or (soap_cat in ('s', 'o', 'a', 'p', 'u')));


-- clin.soap_cat_ranks
alter table clin.soap_cat_ranks	drop constraint if exists clin_soap_cat_ranks_sane_cats;

alter table clin.soap_cat_ranks
	add constraint clin_soap_cat_ranks_sane_cats check
		((soap_cat is NULL) or (soap_cat in ('s', 'o', 'a', 'p', 'u')));


-- clin.clin_narrative
drop index if exists clin.idx_narrative_soap_cat cascade;

create index idx_narrative_soap_cat on clin.clin_narrative(soap_cat) where (soap_cat in ('s', 'o', 'a', 'p', 'u'));

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-lowercase_soap_cat.sql', '22.0');
