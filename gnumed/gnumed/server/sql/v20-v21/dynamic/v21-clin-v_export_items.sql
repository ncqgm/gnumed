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
drop view if exists clin.v_export_items cascade;

create view clin.v_export_items as
select
	inner_export_items.*,
	d_vp.title,
	d_vp.firstnames,
	d_vp.lastnames,
	d_vp.preferred,
	d_vp.gender,
	d_vp.dob
from (
	select
		c_ei.pk
			as pk_export_item,
		coalesce (
			c_ei.fk_identity,
			(select fk_patient from clin.encounter where
				pk = (
					select fk_encounter from blobs.doc_med where pk = (
						select fk_doc from blobs.doc_obj where pk = c_ei.fk_doc_obj
					)
				)
			)
		)	as pk_identity,
		coalesce (
			(select short_alias from dem.staff where db_user = c_ei.created_by),
			c_ei.created_by
		)
			as created_by,
		c_ei.created_when
			as created_when,
		c_ei.designation
			as designation,
		c_ei.description
			as description,
		c_ei.fk_doc_obj
			as pk_doc_obj,
		md5(coalesce (
			c_ei.data,
			coalesce (
				(select b_do.data from blobs.doc_obj b_do where b_do.pk = c_ei.fk_doc_obj),
				''
			)
		)) as md5_sum,
		octet_length(coalesce(c_ei.data, ''::bytea)) as size,
		coalesce (
			c_ei.filename,
			(select b_do.filename from blobs.doc_obj b_do where b_do.pk = c_ei.fk_doc_obj)
		) as filename,
		c_ei.xmin
			as xmin_export_item
	from
		clin.export_item c_ei
	) as inner_export_items
	join dem.v_all_persons d_vp on d_vp.pk_identity = inner_export_items.pk_identity
;


revoke all on clin.v_export_items from public;
grant select on clin.v_export_items to group "gm-staff";

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-clin-v_export_items.sql', '21.0');
