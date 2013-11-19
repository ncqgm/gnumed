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
alter table dem.lnk_org_unit2ext_id drop constraint if exists lnk_org_unit2ext_id_fk_org_unit_fkey cascade;
alter table dem.lnk_org_unit2ext_id drop constraint if exists lnk_org_unit2ext_id_fk_org_unit_fkey1 cascade;


alter table dem.lnk_org_unit2ext_id
	add constraint lnk_org_unit2ext_id_fk_org_unit_fkey
		foreign key (fk_org_unit)
			references dem.org_unit(pk)
			on update cascade
			on delete restrict
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-dem-lnk_org_unit2ext_id-fixup.sql', '19.1');
