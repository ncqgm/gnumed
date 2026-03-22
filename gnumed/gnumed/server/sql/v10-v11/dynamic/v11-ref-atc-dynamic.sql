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
comment on table ref.atc_staging is
'used for importing ATC data';

-- --------------------------------------------------------------
comment on table ref.atc is
'holds ATC data';

comment on column ref.atc.code is
'holds the ATC code';

comment on column ref.atc.term is
'the name of the drug component';

comment on column ref.atc.ddd is
'the Defined Daily Dosage';

comment on column ref.atc.unit is
'the unit on the DDD';

comment on column ref.atc.administration_route is
'by what route this drug is to be given';

comment on column ref.atc.comment is
'a comment on this ATC';

-- --------------------------------------------------------------
drop view if exists ref.v_atc cascade;

create view ref.v_atc as
select
	a.pk as pk_atc,
	a.code as atc,
	a.term,
	a.ddd,
	a.unit,
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

-- --------------------------------------------------------------
grant select on
	ref.atc
--	, ref.atc_pkey
	, ref.v_atc
to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-ref-atc-dynamic.sql,v $', '$Revision: 1.2 $');
