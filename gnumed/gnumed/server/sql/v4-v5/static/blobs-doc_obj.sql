-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
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
select public.log_script_insertion('$RCSfile: blobs-doc_obj.sql,v $', '$Revision: 1.1 $');
