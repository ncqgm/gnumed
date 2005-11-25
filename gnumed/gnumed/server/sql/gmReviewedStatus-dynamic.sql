-- =============================================
-- GNUmed - tracking of reviewed status of incoming data
-- =============================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmReviewedStatus-dynamic.sql,v $
-- $Id: gmReviewedStatus-dynamic.sql,v 1.2 2005-11-25 15:07:28 ncq Exp $
-- license: GPL
-- author: Karsten.Hilbert@gmx.net

-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ---------------------------------------------
-- clin.review__root
comment on table clin.review_root is
	'this table tracks whether a particular clinical item
	 was reviewed by a clinician or not';
comment on column clin.review_root.fk_reviewed_row is
	'the row the review status is for: to be qualified
	 as a proper foreign key in child tables';
comment on column clin.review_root.fk_reviewer is
	'who has reviewed the item';
comment on column clin.review_root.is_technically_abnormal is
	'whether test provider flagged this result as abnormal,
	 *not* a clinical assessment but rather a technical one
	 LDT: exist(8422)';
comment on column clin.review_root.clinically_relevant is
	'whether this result is considered relevant clinically,
	 need not correspond to the value of "techically_abnormal"
	 since abnormal values may be irrelevant while normal
	 ones can be of significance';

-- rules !

-- ---------------------------------------------
-- review root child tables
comment on table clin.reviewed_test_results is
	'review table for test results';
comment on table blobs.reviewed_doc_objs is
	'review table for documents - per page !';

-- ---------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_reviewed_items cascade;
\set ON_ERROR_STOP 1

create view clin.v_reviewed_items as
select
	rr.pk as pk_review_root,
	rr.fk_reviewed_row as pk_reviewed_row,
	rr.fk_reviewer as pk_reviewer,
	rr.is_technically_abnormal as is_technically_abnormal,
	rr.clinically_relevant as clinically_relevant,
	case when ((select 1 from v_staff where pk_identity = rr.fk_reviewer) is null)
		then '<' || rr.fk_reviewer || '>'
		else (select sign from v_staff where pk_identity = rr.fk_reviewer)
	end as reviewer,
	(select relname
	 from pg_class
	 where pg_class.oid = rr.tableoid
	) as src_table
from
	clin.review_root rr
;

-- =============================================
grant SELECT, UPDATE, INSERT, DELETE on
	clin.review_root
	, clin.review_root_pk_seq
	, clin.reviewed_test_results
	, blobs.reviewed_doc_objs
to group "gm-doctors";

grant select on
	clin.v_reviewed_items
to group "gm-doctors";

-- =============================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmReviewedStatus-dynamic.sql,v $', '$Revision: 1.2 $');

-- =============================================
-- $Log: gmReviewedStatus-dynamic.sql,v $
-- Revision 1.2  2005-11-25 15:07:28  ncq
-- - create schema "clin" and move all things clinical into it
--
-- Revision 1.1  2005/10/26 21:31:07  ncq
-- - review status tracking
--
--
