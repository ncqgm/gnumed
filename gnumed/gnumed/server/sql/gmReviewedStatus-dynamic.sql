-- =============================================
-- GNUmed - tracking of reviewed status of incoming data
-- =============================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmReviewedStatus-dynamic.sql,v $
-- $Id: gmReviewedStatus-dynamic.sql,v 1.6 2006-02-02 16:46:12 ncq Exp $
-- license: GPL v2 or later
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

-- =============================================
drop view if exists clin.v_reviewed_items cascade;

create view clin.v_reviewed_items as
select
	(select relnamespace from pg_class where pg_class.oid = rr.tableoid)
		as src_schema,
	(select relname from pg_class where pg_class.oid = rr.tableoid)
		as src_table,
	rr.fk_reviewed_row as pk_reviewed_row,
	rr.is_technically_abnormal as is_technically_abnormal,
	rr.clinically_relevant as clinically_relevant,
	(select short_alias from dem.v_staff where pk_staff = rr.fk_reviewer)
		as reviewer,
	rr.comment,
	rr.pk as pk_review_root,
	rr.fk_reviewer as pk_reviewer
from
	clin.review_root rr
;

-- =============================================
grant SELECT, UPDATE, INSERT, DELETE on
	clin.review_root
	, clin.review_root_pk_seq
to group "gm-doctors";

grant select on
	clin.v_reviewed_items
to group "gm-doctors";

-- =============================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmReviewedStatus-dynamic.sql,v $', '$Revision: 1.6 $');
