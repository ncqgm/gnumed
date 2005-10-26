-- =============================================
-- GNUmed - tracking of reviewed status of incoming data
-- =============================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmReviewedStatus-static.sql,v $
-- $Id: gmReviewedStatus-static.sql,v 1.1 2005-10-26 21:31:08 ncq Exp $
-- license: GPL
-- author: Karsten.Hilbert@gmx.net

-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ---------------------------------------------
create table review_root (
	pk serial primary key,
	fk_reviewed_row integer
		not null,
	fk_reviewer integer
		not null
		references public.xlnk_identity(xfk_identity),
	is_technically_abnormal boolean
		not null,
	clinically_relevant boolean
		not null,
	comment text
		default null,
	unique (fk_reviewed_row, fk_reviewer)
) inherits (audit_fields);

-- ---------------------------------------------
create table reviewed_test_results (
	primary key (pk),
	foreign key (fk_reviewed_row) references test_result(pk),
	unique (fk_reviewed_row, fk_reviewer)
) inherits (review_root);

create table reviewed_doc_objs (
	primary key (pk),
	foreign key (fk_reviewed_row) references blobs.doc_obj(id),
	unique (fk_reviewed_row, fk_reviewer)
) inherits (review_root);

-- =============================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmReviewedStatus-static.sql,v $', '$Revision: 1.1 $');

-- =============================================
-- $Log: gmReviewedStatus-static.sql,v $
-- Revision 1.1  2005-10-26 21:31:08  ncq
-- - review status tracking
--
--
