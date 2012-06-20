-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v11-clin-hospital_stay-dynamic.sql,v 1.3 2009-07-16 09:53:19 ncq Exp $
-- $Revision: 1.3 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on table clin.hospital_stay is
'collects data on hospitalisations of patients, reasons are linked via a link table';

select gm.add_table_for_notifies('clin', 'hospital_stay');
select audit.add_table_for_audit('clin', 'hospital_stay');



comment on column clin.hospital_stay.clin_when is
'to be used as when the patient was admitted';



comment on column clin.hospital_stay.narrative is
'the hospital to which the patient was admitted';

alter table clin.hospital_stay
	add constraint sane_hospital check (
		gm.is_null_or_non_empty_string(narrative)
	);



alter table clin.hospital_stay
	alter column soap_cat
		set default null;



comment on column clin.hospital_stay.discharge is
'when was the patient discharged';

alter table clin.hospital_stay
	alter column discharge
		set default null
;



alter table clin.hospital_stay
	add constraint sane_duration check (
		(discharge is null)
			or
		(discharge > clin_when)
	)
;

-- --------------------------------------------------------------
grant select, insert, update, delete on
	clin.hospital_stay
to group "gm-doctors";

grant select, usage, update on
	clin.hospital_stay_pk_seq
to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v11-clin-hospital_stay-dynamic.sql,v $', '$Revision: 1.3 $');

-- ==============================================================
-- $Log: v11-clin-hospital_stay-dynamic.sql,v $
-- Revision 1.3  2009-07-16 09:53:19  ncq
-- - proper sequence grants
--
--
