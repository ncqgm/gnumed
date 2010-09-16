-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1
set default_transaction_read_only to off;

-- --------------------------------------------------------------
select i18n.upd_tx('de', 'meningococcus A', 'Meningokokken Typ A');
select i18n.upd_tx('de', 'meningococcus W', 'Meningokokken Typ W');
select i18n.upd_tx('de', 'meningococcus Y', 'Meningokokken Typ Y');

select i18n.upd_tx('de', 'tuberculosis', 'Tuberkulose');
select i18n.upd_tx('de', 'salmonella typhi (typhoid)', 'Salmonella typhi (Typhus)');

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v15-i18n-de.sql,v $', '$Revision: 1. $');

-- ==============================================================
