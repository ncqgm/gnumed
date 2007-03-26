-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v4
-- Target database version: v5
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: clin-allergy.sql,v 1.1 2007-03-26 16:47:21 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin._enum_allergy_type
	rename column id to pk;


alter table clin.allergy
	rename column id to pk;

alter table clin.allergy
	rename column id_type to fk_type;


alter table audit.log_allergy
	rename column id to pk;

alter table audit.log_allergy
	rename column id_type to fk_type;


-- --------------------------------------------------------------
-- don't forget appropriate grants
--grant select on forgot_to_edit_grants to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: clin-allergy.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: clin-allergy.sql,v $
-- Revision 1.1  2007-03-26 16:47:21  ncq
-- - renaming columns is static, also remember log tables
--
-- Revision 1.2  2007/03/21 08:14:55  ncq
-- - rename columns
--
-- Revision 1.1  2007/03/18 13:37:47  ncq
-- - add trigger to sync allergic state to allergy content
--
--
