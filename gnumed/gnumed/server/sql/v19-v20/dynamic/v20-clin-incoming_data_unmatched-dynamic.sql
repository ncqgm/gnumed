-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- .fk_identity
alter table clin.incoming_data_unmatched drop constraint if exists incoming_data_unmatched_fk_identity_disambiguated_fkey cascade;
alter table clin.incoming_data_unmatched drop constraint if exists FK_incoming_data_unmatched_fk_identity_disambiguated cascade;

alter table clin.incoming_data_unmatched
	add constraint FK_incoming_data_unmatched_fk_identity_disambiguated foreign key (fk_identity_disambiguated)
		references clin.patient(fk_identity)
		on update cascade
		on delete restrict
;

-- ==============================================================
select gm.log_script_insertion('v20-clin-incoming_data_unmatched-dynamic.sql', '20.0');
