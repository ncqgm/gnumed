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
-- .fk_identity / .fk_doc_obj
-- drop sanity constraint
alter table clin.export_item
	drop constraint if exists
		clin_export_item_fk_obj_or_fk_identity cascade;

-- update existing rows
update clin.export_item c_ei set
	fk_identity = (
		SELECT fk_patient FROM clin.encounter
		WHERE
			pk = (
				SELECT fk_encounter FROM blobs.doc_med WHERE pk = (
					SELECT fk_doc FROM blobs.doc_obj WHERE pk = c_ei.fk_doc_obj
				)
			)
	)
where
	c_ei.fk_doc_obj IS DISTINCT FROM NULL
		AND
	c_ei.fk_identity IS NULL
;

-- set NOT NULL
alter table clin.export_item
	alter column fk_identity
		set not null;

-- --------------------------------------------------------------
-- add trigger to normalize .fk_identity
drop function if exists clin.trf_ins_upd_export_item_normalize_fk_identity() cascade;

create or replace function clin.trf_ins_upd_export_item_normalize_fk_identity()
	returns trigger
	language 'plpgsql'
	as '
BEGIN
	SELECT fk_patient INTO STRICT NEW.fk_identity
	FROM clin.encounter
	WHERE
		pk = (
			SELECT fk_encounter FROM blobs.doc_med WHERE pk = (
				SELECT fk_doc FROM blobs.doc_obj WHERE pk = NEW.fk_doc_obj
			)
		)
	;
	RETURN NEW;
END;';

comment on function clin.trf_ins_upd_export_item_normalize_fk_identity() is
	'Set .fk_identity from .fk_doc if .fk_doc is NOT NULL';

create trigger tr_ins_upd_export_item_normalize_fk_identity
	before
		insert or update
	on
		clin.export_item
	for
		each row
	when
		(NEW.fk_doc_obj IS NOT NULL)
	execute procedure
		clin.trf_ins_upd_export_item_normalize_fk_identity()
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-clin-export_item-dynamic.sql', '22.0');
