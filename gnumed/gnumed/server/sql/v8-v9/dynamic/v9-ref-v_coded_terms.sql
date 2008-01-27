-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-ref-v_coded_terms.sql,v 1.1 2008-01-27 21:06:30 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
\set check_function_bodies 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view ref.v_coded_terms cascade;
\set ON_ERROR_STOP 1


create view ref.v_coded_terms as
select
	code,
	description as term,
	(select name_short from ref.data_source rds where rds.pk = fk_data_source) as coding_system
from
	ref.atc_group

	union

select
	code,
	description as term,
	(select name_short from ref.data_source rds where rds.pk = fk_data_source) as coding_system
from
	ref.atc_substance
;

grant select on ref.v_coded_terms to group "gm-doctors";

comment on view ref.v_coded_terms is
	'This view aggregates all official (reference) terms
	 for which a corresponding code is known to the system.';

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-ref-v_coded_terms.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v9-ref-v_coded_terms.sql,v $
-- Revision 1.1  2008-01-27 21:06:30  ncq
-- - add new
--
--