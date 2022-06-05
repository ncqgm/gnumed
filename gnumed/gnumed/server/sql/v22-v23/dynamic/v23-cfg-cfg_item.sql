-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
comment on table cfg.cfg_template is 'This table defines known configuration options.';

alter table cfg.cfg_template
	drop column if exists type cascade;

alter table cfg.cfg_template
	drop column if exists cfg_group cascade;

-- --------------------------------------------------------------
comment on table cfg.cfg_item is 'This table holds configuration options.';

alter table cfg.cfg_item
	drop column if exists value cascade;

alter table cfg.cfg_item
	add column if not exists
		value jsonb;

comment on column cfg.cfg_item.value is 'The value for this configuration option.';

-- --------------------------------------------------------------
alter table cfg.cfg_item
	alter column owner
		drop not null;

-- --------------------------------------------------------------
-- transfer data

-- strings
update cfg.cfg_item
set value = to_jsonb(c_cs.value)
from cfg.cfg_string c_cs
where c_cs.fk_item = cfg.cfg_item.pk;

-- string lists
update cfg.cfg_item
set value = to_jsonb(c_csa.value)
from cfg.cfg_str_array c_csa
where c_csa.fk_item = cfg.cfg_item.pk;

-- numeric
update cfg.cfg_item
set value = to_jsonb(c_cn.value)
from cfg.cfg_numeric c_cn
where c_cn.fk_item = cfg.cfg_item.pk;

-- data
update cfg.cfg_item
set value = to_jsonb(c_cd.value)
from cfg.cfg_data c_cd
where c_cd.fk_item = cfg.cfg_item.pk;

-- sanitize data
delete from cfg.cfg_item where value is null;

update cfg.cfg_item
set owner = NULL
where owner = 'xxxDEFAULTxxx';

update cfg.cfg_item
set workplace = NULL
where workplace = 'xxxDEFAULTxxx';

update cfg.cfg_item
set cookie = NULL
where cookie = 'xxxDEFAULTxxx';

delete from cfg.cfg_item
where fk_template in (
	select pk from cfg.cfg_template where name ilike 'main.%'
);

delete from cfg.cfg_template where name ilike 'main.%';

-- --------------------------------------------------------------
alter table cfg.cfg_item
	alter column value
		set not null;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-cfg-cfg_item.sql', 'v23');
