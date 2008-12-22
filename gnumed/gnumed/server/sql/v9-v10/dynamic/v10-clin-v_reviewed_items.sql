-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v10-clin-v_reviewed_items.sql,v 1.1 2008-12-22 18:55:18 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_reviewed_items cascade;
\set ON_ERROR_STOP 1


create view clin.v_reviewed_items as
select
	(select relnamespace from pg_class where pg_class.oid = rr.tableoid)
		as src_schema,
	(select relname from pg_class where pg_class.oid = rr.tableoid)
		as src_table,
	rr.fk_reviewed_row
		as pk_reviewed_row,
	rr.is_technically_abnormal
		as is_technically_abnormal,
	rr.clinically_relevant
		as clinically_relevant,
	(select short_alias from dem.staff where pk = rr.fk_reviewer)
		as reviewer,
	rr.comment,
	rr.pk
		as pk_review_root,
	rr.fk_reviewer
		as pk_reviewer
from
	clin.review_root rr
;


comment on view clin.v_reviewed_items is 'denormalization of parent table of reviewed items';


revoke all on clin.v_reviewed_items from public;
grant select on clin.v_reviewed_items to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-clin-v_reviewed_items.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v10-clin-v_reviewed_items.sql,v $
-- Revision 1.1  2008-12-22 18:55:18  ncq
-- - were dropped
--
--