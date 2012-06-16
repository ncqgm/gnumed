-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
-- $Id: v11-ref-v_coded_terms.sql,v 1.2 2009-06-10 21:06:07 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

set default_transaction_read_only to off;
set check_function_bodies to on;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view ref.v_coded_terms cascade;
\set ON_ERROR_STOP 1


create view ref.v_coded_terms as
select
	code,
	term,
	rds.name_short
		as coding_system,
	rds.name_long
		as coding_system_long,
	rds.version,
	rds.lang
from
	ref.coding_system_root rcs
		inner join ref.data_source rds on rcs.fk_data_source = rds.pk
;


grant select on ref.v_coded_terms to group "gm-doctors";

comment on view ref.v_coded_terms is
'This view aggregates all official (reference) terms for which a corresponding code is known to the system.';

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-ref-v_coded_terms.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v11-ref-v_coded_terms.sql,v $
-- Revision 1.2  2009-06-10 21:06:07  ncq
-- - add language, long name, version
--
-- Revision 1.1  2009/06/09 14:52:20  ncq
-- - first version
--
--