-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- .fk_primary_provider
comment on column dem.identity.fk_primary_provider is
'The doctor within this praxis primarily responsible for this patient.';


alter table dem.identity
	add foreign key (fk_primary_provider)
		references dem.staff(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
select gm.log_script_insertion('v15-dem-identity-dynamic.sql', 'Revision: 1.1');
