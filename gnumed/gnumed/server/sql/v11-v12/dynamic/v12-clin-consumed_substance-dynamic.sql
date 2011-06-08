-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v12-clin-consumed_substance-dynamic.sql,v 1.1 2009-10-21 08:50:39 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
select audit.add_table_for_audit('clin', 'consumed_substance');
select gm.add_table_for_notifies('clin', 'consumed_substance');



comment on table clin.consumed_substance is
	'Substances currently or previously actually being consumed by patients.';


comment on column clin.consumed_substance.description is
	'human-readable description of substance';

comment on column clin.consumed_substance.atc_code is
	'NULL or ATC code of substance.';



-- .description
\unset ON_ERROR_STOP
alter table clin.consumed_substance drop constraint unique_description cascade;
alter table clin.consumed_substance drop constraint sane_description cascade;
\set ON_ERROR_STOP 1

alter table clin.consumed_substance
	add constraint unique_description UNIQUE (description);

alter table clin.consumed_substance
	alter column description
		set not null;

alter table clin.consumed_substance
	add constraint sane_description
		check (gm.is_null_or_blank_string(description) is false)
;



-- .atc_code
\unset ON_ERROR_STOP 1
drop index idx_consumed_substance_atc cascade;
\set ON_ERROR_STOP 1

create index idx_consumed_substance_atc on clin.consumed_substance(atc_code);



-- permissions
grant select, insert, update, delete on
	clin.consumed_substance,
	clin.consumed_substance_pk_seq
to group "gm-doctors";



-- move data
insert into clin.consumed_substance (description, atc_code) select description, atc_code from clin.active_substance;

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v12-clin-consumed_substance-dynamic.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v12-clin-consumed_substance-dynamic.sql,v $
-- Revision 1.1  2009-10-21 08:50:39  ncq
-- - new table
--
--