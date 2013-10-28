-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
set check_function_bodies to "on";
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop function blobs.delete_document(integer, integer) cascade;
\set ON_ERROR_STOP 1

create or replace function blobs.delete_document(integer, integer)
	returns boolean
	security definer
	language 'plpgsql'
	as E'
DECLARE
	_pk_doc alias for $1;
	_pk_encounter alias for $2;
	_del_note text;
	_doc_row record;
	_obj_row record;
	tmp text;
BEGIN
	select * into _doc_row from blobs.doc_med where pk = _pk_doc;

	_del_note := _(''Deletion of document'') || E'':\n''
		|| '' ''
			|| to_char(_doc_row.clin_when, ''YYYY-MM-DD HH24:MI'')
			|| '' "'' || (select _(dt.name) from blobs.doc_type dt where pk = _doc_row.fk_type) || ''"''
			|| coalesce('' ('' || _doc_row.ext_ref || '')'', '''')
		|| coalesce(E''\n '' || _doc_row.comment, '''')
	;

	FOR _obj_row IN
		select
			seq_idx,
			comment,
			filename,
			octet_length(coalesce(data, ''''::bytea)) as size,
			md5(coalesce(data, ''''::bytea)) as md5_sum
		from blobs.doc_obj
		where fk_doc = _pk_doc
		order by seq_idx
	LOOP
		_del_note := _del_note || E''\n''
			|| '' #'' || coalesce(_obj_row.seq_idx, ''-1'') || '': "'' || coalesce(_obj_row.comment, '''') || E''"\n''
			|| coalesce(''  file: '' || _obj_row.filename || E''\n'', '''')
			|| ''  size: '' || _obj_row.size || '' bytes / MD5: '' || _obj_row.md5_sum || E''\n'';
	end LOOP;

	insert into clin.clin_narrative
		(fk_encounter, fk_episode, narrative, soap_cat)
	values (
		_pk_encounter,
		_doc_row.fk_episode,
		_del_note,
		NULL
	);

	-- should auto-cascade:
	--delete from blobs.doc_obj where fk_doc = _pk_doc;
	-- should auto-NULL:
	--bill.bill.fk_doc
	delete from blobs.doc_med where pk = _pk_doc;

	return True;
END;';

revoke delete on blobs.doc_med from "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-blobs-delete_document.sql', '19.0');
