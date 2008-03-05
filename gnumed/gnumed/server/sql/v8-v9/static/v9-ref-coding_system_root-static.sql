-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v9-ref-coding_system_root-static.sql,v 1.1 2008-03-05 22:36:11 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
create table ref.coding_system_root (
	pk_coding_system serial
		primary key,
	code text
		not null,
	term text
		not null,
	fk_data_source integer
		not null
		references ref.data_source(pk)
		on update cascade
		on delete restrict,
	comment text,
	unique(fk_data_source, code),
	unique(fk_data_source, term)
);

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v9-ref-coding_system_root-static.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v9-ref-coding_system_root-static.sql,v $
-- Revision 1.1  2008-03-05 22:36:11  ncq
-- - new
--
--