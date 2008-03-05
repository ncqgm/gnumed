-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-ref-coding_system_root-dynamic.sql,v 1.1 2008-03-05 22:35:14 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
grant select, insert, update, delete on
	ref.coding_system_root,
	ref.coding_system_root_pk_seq
to group "gm-doctors";


comment on table ref.coding_system_root is
'Base table for coding system tables providing common fields.';
comment on column ref.coding_system_root.fk_data_source is
'links to the data source for the external reference data set';
comment on column ref.coding_system_root.comment is
'an arbitrary comment on the code and/or term,
 child tables will use this in different ways';

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-ref-coding_system_root-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v9-ref-coding_system_root-dynamic.sql,v $
-- Revision 1.1  2008-03-05 22:35:14  ncq
-- - added
--
--