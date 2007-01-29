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
-- $Id: blobs-doc_obj.sql,v 1.1 2007-01-29 11:53:50 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
--\unset ON_ERROR_STOP
--drop forgot_to_edit_drops;
--\set ON_ERROR_STOP 1

-- add column for file name
alter table blobs.doc_obj
	add column filename text;

alter table blobs.doc_obj
	alter column filename
		set default null;

comment on column blobs.doc_obj.filename is
	'the filename from when the data was imported - if any, can be NULL,
	 useful for re-export since legacy devices/applications might expect
	 particular file names and not use mime types for file detection';

-- --------------------------------------------------------------
-- don't forget appropriate grants
--grant select on forgot_to_edit_grants to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('$RCSfile: blobs-doc_obj.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: blobs-doc_obj.sql,v $
-- Revision 1.1  2007-01-29 11:53:50  ncq
-- - add filename column to blobs.doc_obj
--
-- Revision 1.5  2006/10/24 13:09:45  ncq
--