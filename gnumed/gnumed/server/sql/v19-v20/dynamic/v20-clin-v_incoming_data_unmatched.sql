-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop view if exists clin.v_incoming_data_unmatched cascade;

create view clin.v_incoming_data_unmatched as
select
	c_idu.pk
		as pk_incoming_data_unmatched,
	c_idu.fk_patient_candidates
		as pk_patient_candidates,
	c_idu.firstnames,
	c_idu.lastnames,
	c_idu.dob,
	c_idu.gender,
	c_idu.postcode,
	c_idu.other_info,
	c_idu.request_id,
	c_idu.requestor,
	c_idu.external_data_id,
	c_idu.comment,
	c_idu.fk_identity_disambiguated
		as pk_identity_disambiguated,
	c_idu.fk_provider_disambiguated
		as pk_provider_disambiguated,
	c_idu.type
		as data_type,
	md5(c_idu.data)
		as md5_sum,
	octet_length(c_idu.data)
		as data_size,
	c_idu.xmin
		as xmin_incoming_data_unmatched
from
	clin.incoming_data_unmatched c_idu
;


comment on view clin.v_incoming_data_unmatched is
	'Shows incoming data but w/o the data field.';


grant select on clin.v_incoming_data_unmatched to group "gm-doctors";

-- ==============================================================
select gm.log_script_insertion('v20-clin-v_incoming_data_unmatched.sql', '20.0');
