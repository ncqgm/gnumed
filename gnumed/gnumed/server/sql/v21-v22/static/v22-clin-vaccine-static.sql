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
alter table clin.vaccine
	rename column fk_brand to fk_drug_product;

alter table audit.log_vaccine
	rename column fk_brand to fk_drug_product;

-- disable audit triggers because table has changed so
-- audit trigger won't work anymore
drop function audit.ft_del_vaccine() cascade;
drop function audit.ft_ins_vaccine() cascade;
drop function audit.ft_upd_vaccine() cascade;

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-vaccine-static.sql', '22.0');
