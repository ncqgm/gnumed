-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- .atc_mono_indication
alter table clin.vacc_indication
	add column atcs_mono_indication text[];

alter table audit.log_vacc_indication
	add column atcs_mono_indication text[];


-- .atcs_poly_indication
alter table clin.vacc_indication
	add column atcs_poly_indication text[];

alter table audit.log_vacc_indication
	add column atcs_poly_indication text[];
-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v14-clin-vacc_indication-static.sql,v $', '$Revision: 1.1 $');
