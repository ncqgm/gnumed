-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: 
--
-- ==============================================================
-- $Id: zzz-template.sql,v 1.10 2008-12-12 16:37:44 ncq Exp $
-- $Revision: 1.10 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- remember to handle dependant objects possibly dropped by CASCADE
\unset ON_ERROR_STOP
drop forgot_to_edit_drops cascade;
\set ON_ERROR_STOP 1


comment on column/table .forgot_to_edit_comment. is
	'';

-- --------------------------------------------------------------
-- don't forget appropriate grants
grant select, insert, update, delete on
	.forgot_to_edit_grants
to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: zzz-template.sql,v $', '$Revision: 1.10 $');

-- ==============================================================
-- $Log: zzz-template.sql,v $
-- Revision 1.10  2008-12-12 16:37:44  ncq
-- - somewhat improve presets
--
-- Revision 1.9  2008/07/15 16:49:46  ncq
-- - add default transaction handling
--
-- Revision 1.8  2008/05/29 15:33:27  ncq
-- - no more source/target db version
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
