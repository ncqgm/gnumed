-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten.Hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
alter table dem.inbox_item_type
	drop constraint if exists inbox_item_type_description_key cascade;

alter table dem.inbox_item_type
	drop constraint if exists inbox_item_type_uniq_desc_cat cascade;

alter table dem.inbox_item_type
	add constraint inbox_item_type_uniq_desc_cat unique (description, fk_inbox_item_category);

-- --------------------------------------------------------------
update dem.inbox_item_type set
	fk_inbox_item_category = (
		select pk from dem.inbox_item_category
		where description = 'administrative'
	)
where
	description in (
		'Privacy notice',
		'Datenschutzhinweis'
	)
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-dem-provider_inbox-dynamic.sql', '19.0');
