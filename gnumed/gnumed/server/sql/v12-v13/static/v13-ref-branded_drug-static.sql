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
-- .external_code_type
alter table ref.branded_drug
	add column external_code_type text;

alter table audit.log_branded_drug
	add column external_code_type text;

update ref.branded_drug set
	external_code_type = trim(leading ':' from substring(external_code from '::.+$'))
;

update ref.branded_drug set
	external_code = substring(external_code from '^[^:]+')
;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v13-ref-drug-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
