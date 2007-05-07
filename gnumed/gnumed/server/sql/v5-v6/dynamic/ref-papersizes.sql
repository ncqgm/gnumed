-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v5
-- Target database version: v6
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: ref-papersizes.sql,v 1.1 2007-05-07 16:26:22 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on column ref.papersizes.size is '(cm, cm)';

grant select on ref.papersizes to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: ref-papersizes.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: ref-papersizes.sql,v $
-- Revision 1.1  2007-05-07 16:26:22  ncq
-- - moved from public
--
--
