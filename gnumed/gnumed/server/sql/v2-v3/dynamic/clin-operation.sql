-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: clin-operation.sql,v 1.1 2006-12-13 13:33:51 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- remember to handle dependant objects possibly dropped by CASCADE
--\unset ON_ERROR_STOP
--drop forgot_to_edit_drops;
--\set ON_ERROR_STOP 1


--comment on forgot_to_edit_comment is
--	'';

-- --------------------------------------------------------------
-- don't forget appropriate grants
grant select, insert, update, delete on clin.operation to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-operation.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: clin-operation.sql,v $
-- Revision 1.1  2006-12-13 13:33:51  ncq
-- - fix missing permissions
--
-- Revision 1.5  2006/10/24 13:09:45  ncq
-- - What it does duplicates the change log so axe it
--
