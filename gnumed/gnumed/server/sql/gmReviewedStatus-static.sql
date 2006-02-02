-- =============================================
-- GNUmed - tracking of reviewed status of incoming data
-- =============================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmReviewedStatus-static.sql,v $
-- $Id: gmReviewedStatus-static.sql,v 1.6 2006-02-02 16:46:12 ncq Exp $
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
		references dem.staff(pk)
		on update cascade
		on delete restrict,
	is_technically_abnormal boolean
		not null,
	clinically_relevant boolean
		not null,
	comment text
		default null,
	unique (fk_reviewed_row, fk_reviewer)
) inherits (audit.audit_fields);

-- =============================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmReviewedStatus-static.sql,v $', '$Revision: 1.6 $');

-- =============================================
-- $Log: gmReviewedStatus-static.sql,v $
-- Revision 1.6  2006-02-02 16:46:12  ncq
-- - remove signature/key_id/key_context again as discussion
--   proved it to not be necessary (changes should be audited
--   and audits should be timestamped and signed)
--
-- Revision 1.5  2006/01/27 22:27:06  ncq
-- - make review_root.fk_reviewer reference dem.staff(pk)
-- - add signature/key_id/key_context and comments
-- - factor out child tables into their schemata
-- - add source table namespace (schema) to v_reviewed_items
--
-- Revision 1.4  2006/01/11 13:30:57  ncq
-- - id -> pk
--
-- Revision 1.3  2006/01/05 16:04:37  ncq
-- - move auditing to its own schema "audit"
--
-- Revision 1.2  2005/11/25 15:07:28  ncq
-- - create schema "clin" and move all things clinical into it
--
-- Revision 1.1  2005/10/26 21:31:08  ncq
-- - review status tracking
--
--
