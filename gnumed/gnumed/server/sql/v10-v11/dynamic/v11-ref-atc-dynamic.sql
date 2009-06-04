-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v11-ref-atc-dynamic.sql,v 1.1 2009-06-04 17:48:10 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
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
\unset ON_ERROR_STOP
drop view ref.v_atc cascade;
\set ON_ERROR_STOP 1

create view ref.v_atc as
select
	a.pk as pk_atc,
	a.code as atc,
	a.term,
	coalesce (
		i18n.tx_or_null(a.code),
		a.term
	)	as l10n_term,
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

	a.pk_coding_system,
	a.fk_data_source
		as pk_data_source
from
	ref.atc a
		inner join ref.data_source rds on rds.pk = a.fk_data_source
;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-ref-atc-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v11-ref-atc-dynamic.sql,v $
-- Revision 1.1  2009-06-04 17:48:10  ncq
-- - first version
--
--