-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v11-bill-schema.sql,v 1.1 2009-03-10 14:29:05 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create schema bill authorization "gm-dbo";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-bill-schema.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v11-bill-schema.sql,v $
-- Revision 1.1  2009-03-10 14:29:05  ncq
-- - new
--
--