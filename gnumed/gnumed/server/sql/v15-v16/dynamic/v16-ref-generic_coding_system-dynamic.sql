-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
select gm.register_notifying_table('ref', 'generic_coding_system');

comment on table ref.generic_coding_system is
'Holding codes from all coding systems.

Some ideas by Ian Haywood, more from the PostgreSQL mailing list.';

-- --------------------------------------------------------------
-- .code
alter table ref.generic_coding_system
	alter column code
		set not null;

\unset ON_ERROR_STOP
alter table ref.generic_coding_system drop constraint ref_generic_uniq_code_per_source cascade;
\set ON_ERROR_STOP 1

alter table ref.generic_coding_system
	add constraint ref_generic_uniq_code_per_source
		unique(code, fk_data_source);

-- --------------------------------------------------------------
-- .term
alter table ref.generic_coding_system
	alter column term
		set not null;

-- --------------------------------------------------------------
-- .fk_data_source
alter table ref.generic_coding_system
	alter column fk_data_source
		set not null;

\unset ON_ERROR_STOP
alter table ref.generic_coding_system drop constraint fk_ref_generic2ref_data_source;
\set ON_ERROR_STOP 1

alter table ref.generic_coding_system
	add foreign key (fk_data_source)
		references ref.data_source(pk)
		on update cascade
		on delete restrict;

\unset ON_ERROR_STOP
drop index idx_ref_generic2ref_data_source_fk cascade;
\set ON_ERROR_STOP 1

create index idx_ref_generic2ref_data_source_fk on ref.generic_coding_system(fk_data_source);

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop index idx_generic_coding_system_npk cascade;
\set ON_ERROR_STOP 1

create unique index idx_generic_coding_system_npk on ref.generic_coding_system(code, term, fk_data_source);

-- --------------------------------------------------------------
grant SELECT on
	ref.generic_coding_system
to "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-ref-generic_coding_system-static.sql', '1.0');
