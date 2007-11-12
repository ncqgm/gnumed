-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v7
-- Target database version: v8
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: blobs-delete_document.sql,v 1.3 2007-11-12 23:11:24 ncq Exp $
-- $Revision: 1.3 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

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

	BEGIN
		select * into _doc_row from blobs.doc_med where pk = _pk_doc;
	EXCEPTION
		when NO_DATA_FOUND then
			return True;
		return FALSE;
	END;

	_del_note := _(''Deletion of document'') || E'':\n''
		|| '' '' || to_char(_doc_row.date, ''YYYY-MM-DD HH24:MI'') || '' "''
		|| (select _(dt.name) from blobs.doc_type dt where pk = _doc_row.fk_type) || ''" (''
		|| _doc_row.ext_ref || E'')\n''
		|| '' '' || coalesce(_doc_row.comment, '''');

	FOR _obj_row IN select * from blobs.doc_obj where fk_doc = _pk_doc order by seq_idx LOOP
		_del_note := _del_note || E''\n''
			|| '' #'' || _obj_row.seq_idx || '': "'' || coalesce(_obj_row.comment, '''') || E''"\n''
			|| '' '' || coalesce(_obj_row.filename, '''') || E''\n'';
	end LOOP;

	insert into clin.clin_narrative
		(fk_encounter, fk_episode, narrative, soap_cat)
	values (
		_pk_encounter,
		_doc_row.fk_episode,
		_del_note,
		NULL
	);

	delete from blobs.doc_med where pk = _pk_doc;

	return True;

END;';


select i18n.i18n('Deletion of document');
select i18n.upd_tx('de_DE', 'Deletion of document', 'Dokument gelöscht');


revoke delete on blobs.doc_med from "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: blobs-delete_document.sql,v $', '$Revision: 1.3 $');

-- ==============================================================
-- $Log: blobs-delete_document.sql,v $
-- Revision 1.3  2007-11-12 23:11:24  ncq
-- - remove strict
--
-- Revision 1.2  2007/11/05 11:40:26  ncq
-- - revoke delete right on blobs.doc_med and make
--   delete_document() security definer
--
-- Revision 1.1  2007/11/05 11:35:56  ncq
-- - new
--
--
