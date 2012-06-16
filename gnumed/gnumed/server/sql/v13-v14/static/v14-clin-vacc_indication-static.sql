-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- .atc_single_indication
alter table clin.vacc_indication
	add column atcs_single_indication text[];

alter table audit.log_vacc_indication
	add column atcs_single_indication text[];


-- .atcs_combi_indication
alter table clin.vacc_indication
	add column atcs_combi_indication text[];

alter table audit.log_vacc_indication
	add column atcs_combi_indication text[];
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v14-clin-vacc_indication-static.sql,v $', '$Revision: 1.1 $');
