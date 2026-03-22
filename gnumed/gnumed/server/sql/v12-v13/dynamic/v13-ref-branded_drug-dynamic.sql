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
-- .external_code
comment on column ref.branded_drug.external_code_type is
	'an opaque code type from an external data source, such as "PZN" in Germany';

alter table ref.branded_drug drop constraint if exists drug_sane_external_code_type cascade;

alter table ref.branded_drug
	add constraint drug_sane_external_code_type
		check (
			((external_code is NULL) and (external_code_type is NULL))
				or
			((external_code is not NULL) and (external_code_type is not NULL))
		);

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v13-ref-drug-dynamic.sql,v $', '$Revision: 1.2 $');
