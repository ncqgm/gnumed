-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
drop function if exists audit.ft_del_doc_med() cascade;
drop function if exists audit.ft_ins_doc_med() cascade;
drop function if exists audit.ft_upd_doc_med() cascade;

-- --------------------------------------------------------------
-- .unit_is_receiver
comment on column blobs.doc_med.unit_is_receiver is 'whether the org unit is the receiver rather than the document source';

alter table blobs.doc_med
	alter column unit_is_receiver
		set default FALSE;

alter table blobs.doc_med
	alter column unit_is_receiver
		set not null;

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-blobs-doc_med-dynamic.sql', '22.0');
