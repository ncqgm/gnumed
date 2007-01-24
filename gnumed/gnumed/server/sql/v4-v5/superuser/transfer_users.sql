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
-- $Id: transfer_users.sql,v 1.1 2007-01-24 10:57:47 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

select gm_transfer_users('gnumed_v4'::text);

-- ==============================================================
-- $Log: transfer_users.sql,v $
-- Revision 1.1  2007-01-24 10:57:47  ncq
-- - need to transfer users as usual
--
--
