-- =============================================
-- GNUmed - tracking of reviewed status of incoming data
-- =============================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmReviewedStatus-static.sql,v $
-- $Id: gmReviewedStatus-static.sql,v 1.3 2006-01-05 16:04:37 ncq Exp $
-- license: GPL
-- author: Karsten.Hilbert@gmx.net

-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ---------------------------------------------
create table clin.review_root (
	pk serial primary key,
	fk_reviewed_row integer
		not null,
	fk_reviewer integer
		not null
		references clin.xlnk_identity(xfk_identity),
	is_technically_abnormal boolean
		not null,
	clinically_relevant boolean
		not null,
	comment text
		default null,
	unique (fk_reviewed_row, fk_reviewer)
) inherits (audit.audit_fields);

-- ---------------------------------------------
create table clin.reviewed_test_results (
	primary key (pk),
	foreign key (fk_reviewed_row) references clin.test_result(pk),
	unique (fk_reviewed_row, fk_reviewer)
) inherits (clin.review_root);

create table blobs.reviewed_doc_objs (
	primary key (pk),
	foreign key (fk_reviewed_row) references blobs.doc_obj(id),
	unique (fk_reviewed_row, fk_reviewer)
) inherits (clin.review_root);

-- =============================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmReviewedStatus-static.sql,v $', '$Revision: 1.3 $');

-- =============================================
-- $Log: gmReviewedStatus-static.sql,v $
-- Revision 1.3  2006-01-05 16:04:37  ncq
-- - move auditing to its own schema "audit"
--
-- Revision 1.2  2005/11/25 15:07:28  ncq
-- - create schema "clin" and move all things clinical into it
--
-- Revision 1.1  2005/10/26 21:31:08  ncq
-- - review status tracking
--
--
