-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
\set ON_ERROR_STOP 1
set check_function_bodies to on;

-- --------------------------------------------------------------
drop view if exists ref.v_coded_terms cascade;


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
