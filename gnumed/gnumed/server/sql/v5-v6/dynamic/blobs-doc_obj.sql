-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v5
-- Target database version: v6
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: blobs-doc_obj.sql,v 1.2 2007-05-07 16:33:06 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- seq_idx
drop function if exists blobs.trf_verify_page_number() cascade;


create function blobs.trf_verify_page_number()
	returns trigger
	language plpgsql
	as '
declare
	msg text;
begin
	if NEW.seq_idx is NULL then
		return NEW;
	end if;

	perform 1 from blobs.doc_obj where pk <> NEW.pk and fk_doc = NEW.fk_doc and seq_idx = NEW.seq_idx;
	if FOUND then
		msg := ''[blobs.trf_verify_page_number]: uniqueness violation: seq_idx ['' || NEW.seq_idx || ''] already exists for fk_doc ['' || NEW.fk_doc || '']'';
		raise exception ''%'', msg;
	end if;
	return NEW;
end;';


create trigger tr_verify_page_number
	before insert or update on blobs.doc_obj
	for each row execute procedure blobs.trf_verify_page_number()
;


-- file name
update blobs.doc_obj
	set filename = NULL
	where
		filename is not NULL and
		trim(filename) = '';

alter table blobs.doc_obj drop constraint if exists "doc_obj_filename_check";

alter table blobs.doc_obj
	add check (trim(coalesce(filename, 'NULL')) <> '');

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: blobs-doc_obj.sql,v $', '$Revision: 1.2 $');
