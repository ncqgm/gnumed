-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on column clin.incoming_data_unmatched.fk_provider_disambiguated is
	'The provider the data is relevant to.';


\unset ON_ERROR_STOP
alter table clin.incoming_data_unmatched drop constraint incoming_data_unmatched_fk_provider_disambiguated_fkey cascade;
\set ON_ERROR_STOP 1

alter table clin.incoming_data_unmatched
	add foreign key (fk_provider_disambiguated)
		references dem.staff(pk)
		on update cascade
		on delete restrict;

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-incoming_data_unmatched-dynamic.sql', '16.0');
