-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v6
-- Target database version: v7
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: clin-form_instances.sql,v 1.1 2007-09-16 22:04:31 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
alter table clin.form_instances
	add foreign key (fk_form_def)
		references ref.paperwork_templates(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: clin-form_instances.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: clin-form_instances.sql,v $
-- Revision 1.1  2007-09-16 22:04:31  ncq
-- - add foreign key
--
-- 