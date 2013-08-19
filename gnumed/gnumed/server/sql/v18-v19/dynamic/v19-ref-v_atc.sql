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
drop view if exists ref.v_atc cascade;

create view ref.v_atc as
select
	a.pk as pk_atc,
	a.code as atc,
	a.term,
	a.administration_route,
	a.comment,
	(octet_length(code) < 7)
		as is_group_code,
	(octet_length(code) - (octet_length(code) / 3))
		as atc_level,

	rds.name_long,
	rds.name_short,
	rds.version,
	rds.lang,

	a.pk_coding_system,
	a.fk_data_source
		as pk_data_source
from
	ref.atc a
		inner join ref.data_source rds on rds.pk = a.fk_data_source
;


grant select on	ref.v_atc to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-ref-v_atc.sql', '19.0');
