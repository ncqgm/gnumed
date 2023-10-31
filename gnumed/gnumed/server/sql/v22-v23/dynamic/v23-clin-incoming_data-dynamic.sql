-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
select gm.register_notifying_table('clin', 'incoming_data');
select audit.register_table_for_auditing('clin', 'incoming_data');

delete from audit.audited_tables where schema = 'clin' and table_name = 'incoming_data_unmatched';
drop function if exists audit.ft_del_incoming_data_unmatched() cascade;
drop function if exists audit.ft_ins_incoming_data_unmatched() cascade;
drop function if exists audit.ft_upd_incoming_data_unmatched() cascade;

-- --------------------------------------------------------------
drop view if exists clin.v_incoming_data_unmatched cascade;
drop view if exists clin.v_incoming_data cascade;

create view clin.v_incoming_data as
select
	c_idu.pk
		as pk_incoming_data,
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
	c_idu.fk_identity
		as pk_identity,
	c_idu.fk_provider_disambiguated
		as pk_provider_disambiguated,
	c_idu.type
		as data_type,
	md5(c_idu.data)
		as md5_sum,
	octet_length(c_idu.data)
		as data_size,
	c_idu.xmin
		as xmin_incoming_data
from
	clin.incoming_data c_idu
;

comment on view clin.v_incoming_data is
	'Shows incoming data but w/o the data field.';

revoke all on clin.v_incoming_data from public;
grant select on clin.v_incoming_data to group "gm-doctors";

-- ==============================================================
select gm.log_script_insertion('v23-clin-incoming_data-dynamic.sql', '23.0');
