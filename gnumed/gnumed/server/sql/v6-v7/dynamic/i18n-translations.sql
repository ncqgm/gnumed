-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v6
-- Target database version: v7
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: i18n-translations.sql,v 1.1 2007-06-12 13:21:14 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
select i18n.upd_tx('de_DE', 'document entry', 'Dokumenteneingang');
select i18n.upd_tx('de_DE', 'Family Hx', 'Familienanamnese');

select i18n.upd_tx('de_DE', 'manager', 'Manager');
select i18n.upd_tx('de_DE', 'X-ray assistant', 'MTRA');
select i18n.upd_tx('de_DE', 'lab technician', 'MTLA');
select i18n.upd_tx('de_DE', 'medical student', 'Medizinstudent');
select i18n.upd_tx('de_DE', 'student nurse', 'Schwesternschüler/-in');
select i18n.upd_tx('de_DE', 'trainee - X-ray', 'MTRA (Azubi)');
select i18n.upd_tx('de_DE', 'trainee - lab', 'MTLA (Azubi)');

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: i18n-translations.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: i18n-translations.sql,v $
-- Revision 1.1  2007-06-12 13:21:14  ncq
-- - new
--
-- Revision 1.7  2007/05/07 16:32:09  ncq
-- - log_script_insertion() now in gm.
--
-- Revision 1.6  2007/01/27 21:16:08  ncq
-- - the begin/commit does not fit into our change script model
--
-- Revision 1.5  2006/10/24 13:09:45  ncq
-- - What it does duplicates the change log so axe it
--
-- Revision 1.4  2006/09/28 14:39:51  ncq
-- - add comment template
--
-- Revision 1.3  2006/09/18 17:32:53  ncq
-- - make more fool-proof
--
-- Revision 1.2  2006/09/16 21:47:37  ncq
-- - improvements
--
-- Revision 1.1  2006/09/16 14:02:36  ncq
-- - use this as a template for change scripts
--
--
