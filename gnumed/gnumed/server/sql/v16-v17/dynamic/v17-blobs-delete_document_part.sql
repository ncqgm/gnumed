-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

set check_function_bodies to "on";

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop function blobs.delete_document_part(integer, integer) cascade;
\set ON_ERROR_STOP 1

create or replace function blobs.delete_document_part(integer, integer)
	returns boolean
	security definer
	language 'plpgsql'
	as E'
DECLARE
	_pk_doc_part alias for $1;
	_pk_encounter alias for $2;
	_del_note text;
	_doc_row record;
	_obj_row record;
	tmp text;
BEGIN
	select * into _obj_row from blobs.doc_obj where pk = _pk_doc_part;
	select * into _doc_row from blobs.doc_med where pk = _obj_row.fk_doc;

	_del_note := _(''Deletion of part from document'') || E'':\n''
		|| '' ''
			|| to_char(_doc_row.clin_when, ''YYYY-MM-DD HH24:MI'')
			|| '' "'' || (select _(dt.name) from blobs.doc_type dt where pk = _doc_row.fk_type) || ''"''
			|| coalesce('' ('' || _doc_row.ext_ref || '')'', '''')
		|| coalesce(E''\n '' || _doc_row.comment, '''')
		|| E''\n''
		|| '' #'' || coalesce(_obj_row.seq_idx, ''-1'') || '': "'' || coalesce(_obj_row.comment, '''') || E''"\n''
		|| '' '' || coalesce(_obj_row.filename, '''') || E''\n''
	;

	insert into clin.clin_narrative
		(fk_encounter, fk_episode, narrative, soap_cat)
	values (
		_pk_encounter,
		_doc_row.fk_episode,
		_del_note,
		NULL
	);

	delete from blobs.doc_obj where pk = _pk_doc_part;

	return True;
END;';

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-blobs-delete_document_part.sql', '17.0');
