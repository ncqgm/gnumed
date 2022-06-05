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
drop view if exists cfg.v_cfg_options cascade;

create view cfg.v_cfg_options as
select
	c_ct.name as option,
	c_ci.value as value,
	c_ct.description as description,
	c_ci.owner as owner,
	c_ci.workplace as workplace,
	c_ci.cookie as cookie,
	c_ct.pk as pk_cfg_template,
	c_ci.pk as pk_cfg_item
from
	cfg.cfg_template c_ct,
	cfg.cfg_item c_ci
where
	c_ci.fk_template = c_ct.pk
;

-- ======================================================
GRANT SELECT ON cfg.v_cfg_options TO GROUP "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-cfg-v_cfg_options.sql', 'v23');
