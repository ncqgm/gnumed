-- =============================================
-- GNUmed - tracking of reviewed status of incoming data
-- =============================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmReviewedStatus-dynamic.sql,v $
-- $Id: gmReviewedStatus-dynamic.sql,v 1.5 2006-01-27 22:27:06 ncq Exp $
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
comment on column clin.review_root.signature is
	'can store a signature over the content referenced by
	 fk_reviewed_row such that that cannot be changed without
	 invalidating the signature';
comment on column clin.review_root.key_id is
	'the "id" of the "key" used to generate the signature';
comment on column clin.review_root.key_context is
	'the context (algorithm etc) by which the key referenced
	 via key_id was applied to the content referenced by
	 fk_reviewed_row to generate the signature';

alter table clin.review_root
	add constraint sig_must_be_fully_qualified check (
		((signature is null) and (key_id is null) and (key_context is null))
			or
		((signature is not null) and (key_id is not null) and (key_context is not null))
	);

-- rules !

-- =============================================
\unset ON_ERROR_STOP
drop view clin.v_reviewed_items cascade;
\set ON_ERROR_STOP 1

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
	rr.signature,
	rr.key_id,
	rr.key_context,
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
select log_script_insertion('$RCSfile: gmReviewedStatus-dynamic.sql,v $', '$Revision: 1.5 $');

-- =============================================
-- $Log: gmReviewedStatus-dynamic.sql,v $
-- Revision 1.5  2006-01-27 22:27:06  ncq
-- - make review_root.fk_reviewer reference dem.staff(pk)
-- - add signature/key_id/key_context and comments
-- - factor out child tables into their schemata
-- - add source table namespace (schema) to v_reviewed_items
--
-- Revision 1.4  2006/01/23 22:10:57  ncq
-- - staff.sign -> .short_alias
--
-- Revision 1.3  2006/01/06 10:12:02  ncq
-- - add missing grants
-- - add_table_for_audit() now in "audit" schema
-- - demographics now in "dem" schema
-- - add view v_inds4vaccine
-- - move staff_role from clinical into demographics
-- - put add_coded_term() into "clin" schema
-- - put German things into "de_de" schema
--
-- Revision 1.2  2005/11/25 15:07:28  ncq
-- - create schema "clin" and move all things clinical into it
--
-- Revision 1.1  2005/10/26 21:31:07  ncq
-- - review status tracking
--
--
