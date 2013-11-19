-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- deduplicate dem.org
update dem.org set
	description = description || ' (#' || pk || ')'
where description in (
	select description from dem.org group by description having count(*) > 1
);

alter table dem.org drop constraint if exists dem_org_uniq_desc cascade;

alter table dem.org
	add constraint dem_org_uniq_desc
		unique (description)
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-dem-org-fixup.sql', '19.1');
