-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on table clin.export_item is 'A table to hold binary data for patients intended for export as print/mail/fax/removable media/...';

select gm.register_notifying_table('clin', 'export_item');

grant select on clin.export_item to group "gm-staff";
grant insert, update, delete on clin.export_item to group "gm-staff";

GRANT USAGE ON SEQUENCE
	clin.export_item_pk_seq
to group "gm-staff";

-- --------------------------------------------------------------
-- .created_by
comment on column clin.export_item.created_by is 'who put this item here';

alter table clin.export_item
	alter column created_by
		set not null;

alter table clin.export_item
	alter column created_by
		set default CURRENT_USER;

alter table clin.export_item drop constraint if exists clin_export_item_sane_by cascade;

alter table clin.export_item
	add constraint clin_export_item_sane_by check (
		length(created_by) > 0
	);

-- --------------------------------------------------------------
-- .created_when
comment on column clin.export_item.created_when is 'when was this item put here';

alter table clin.export_item
	alter column created_when
		set not null;

alter table clin.export_item
	alter column created_when
		set default statement_timestamp();

-- --------------------------------------------------------------
-- .designation
comment on column clin.export_item.designation is 'the intended use for this item if any, say "print" for printing';

alter table clin.export_item drop constraint if exists clin_export_item_sane_designation cascade;

alter table clin.export_item
	add constraint clin_export_item_sane_designation check (
		gm.is_null_or_non_empty_string(designation) is True
	);

-- --------------------------------------------------------------
-- .description
comment on column clin.export_item.description is 'a unique-per-patient description of the item';

alter table clin.export_item drop constraint if exists clin_export_item_sane_description cascade;

alter table clin.export_item
	add constraint clin_export_item_sane_description check (
		gm.is_null_or_blank_string(description) is False
	);

-- --------------------------------------------------------------
-- . fk_doc_obj
comment on column clin.export_item.fk_doc_obj is 'points to a document object';


alter table clin.export_item drop constraint if exists clin_export_item_uniq_fk_obj cascade;

alter table clin.export_item
	add constraint clin_export_item_uniq_fk_obj unique (fk_doc_obj);


alter table clin.export_item drop constraint if exists FK_clin_export_item_fk_doc_obj cascade;

alter table clin.export_item
	add constraint FK_clin_export_item_fk_doc_obj foreign key (fk_doc_obj)
		references blobs.doc_obj(pk)
		on update cascade
		on delete restrict
;

-- --------------------------------------------------------------
-- .data
comment on column clin.export_item.data is 'binary data representing the actual export item (unless fk_doc_obj points to a document object)';

alter table clin.export_item drop constraint if exists clin_export_item_sane_data cascade;

alter table clin.export_item
	add constraint clin_export_item_sane_data check (
		(data is null)
			or
		(length(data) > 0)
	);

-- --------------------------------------------------------------
-- .fk_identity
comment on column clin.export_item.fk_identity is 'the patient this item pertains to, DELETE does not cascade because we may have wanted to export data before deleting a patient ...';

alter table clin.export_item drop constraint if exists FK_clin_export_item_fk_identity cascade;

alter table clin.export_item
	add constraint FK_clin_export_item_fk_identity foreign key (fk_identity)
		references clin.patient(fk_identity)
		on update cascade
		on delete restrict
;

-- --------------------------------------------------------------
-- .filename
comment on column clin.export_item.filename is 'a filename, possibly from an import, if applicable, mainly used to please non-mime pseudo operating systems';

alter table clin.export_item drop constraint if exists clin_export_item_sane_filename cascade;

alter table clin.export_item
	add constraint clin_export_item_sane_filename check (
		gm.is_null_or_non_empty_string(filename) is True
	);

-- --------------------------------------------------------------
-- multi-column constraints

-- unique(fk_identity <-> description)
alter table clin.export_item drop constraint if exists clin_export_item_uniq_desc_per_pat cascade;

alter table clin.export_item
	add constraint clin_export_item_uniq_desc_per_pat unique (fk_identity, description);


-- fk_doc_obj <-> data
alter table clin.export_item drop constraint if exists clin_export_item_fk_obj_or_data cascade;

alter table clin.export_item
	add constraint clin_export_item_fk_obj_or_data check (
		((data is null) and (fk_doc_obj is not null))
			or
		((data is not null) and (fk_doc_obj is null))
	);


-- fk_doc_obj <-> fk_identity
alter table clin.export_item drop constraint if exists clin_export_item_fk_obj_or_fk_identity cascade;

alter table clin.export_item
	add constraint clin_export_item_fk_obj_or_fk_identity check (
		((fk_identity is null) and (fk_doc_obj is not null))
			or
		((fk_identity is not null) and (fk_doc_obj is null))
	);


-- fk_doc_obj <-> filename
alter table clin.export_item drop constraint if exists clin_export_item_fk_obj_or_filename cascade;

alter table clin.export_item
	add constraint clin_export_item_fk_obj_or_filename check (
		((filename is null) and (fk_doc_obj is not null))
			or
		((filename is not null) and (fk_doc_obj is null))
	);

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-clin-export_item-dynamic.sql', '20.0');
