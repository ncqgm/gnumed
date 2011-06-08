-- ======================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/v10-v11/dynamic/v11-i18n-upd_tx-dynamic.sql,v $
-- $Id: v11-i18n-upd_tx-dynamic.sql,v 1.1 2009-07-16 09:38:58 ncq Exp $
-- license: GPL v2 or later
-- author: Karsten.Hilbert@gmx.net
-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
create or replace function i18n.upd_tx(text, text)
	returns boolean
	language sql
	as 'select i18n.upd_tx((select i18n.get_curr_lang()), $1, $2)'
;

-- =============================================
select gm.log_script_insertion('$RCSfile: v11-i18n-upd_tx-dynamic.sql,v $', '$Revision: 1.1 $');

-- =============================================
-- $Log: v11-i18n-upd_tx-dynamic.sql,v $
-- Revision 1.1  2009-07-16 09:38:58  ncq
-- - fix security definer use in two-args version
--
--