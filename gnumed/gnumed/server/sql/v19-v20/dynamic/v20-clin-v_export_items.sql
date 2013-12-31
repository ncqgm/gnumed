-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop view if exists clin.v_export_items cascade;

create view clin.v_export_items as
select
	c_ei.pk
		as pk_export_item,
	c_ei.fk_identity
		as pk_identity,
	coalesce (
		(select short_alias from dem.staff where db_user = c_ei.created_by),
		'<' || c_ei.created_by || '>'
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
	c_ei.xmin
		as xmin_export_item
from
	clin.export_item c_ei
;


grant select on clin.v_export_items to group "gm-staff";

-- --------------------------------------------------------------
select gm.log_script_insertion('v20-clin-v_export_items.sql', '20.0');
