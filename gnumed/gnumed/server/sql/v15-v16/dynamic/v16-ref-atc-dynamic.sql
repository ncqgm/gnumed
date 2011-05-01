-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- table-level definitions
comment on table ref.atc is
'holds ATC data';


select gm.register_notifying_table('ref', 'atc');


\unset ON_ERROR_STOP
alter table ref.atc drop constraint fk_ref_atc2ref_generic;
\set ON_ERROR_STOP 1

alter table ref.atc
	add foreign key (code, term, fk_data_source)
		references ref.generic_coding_system(code, term, fk_data_source)
		match full
		on update restrict
		on delete restrict;


\unset ON_ERROR_STOP
drop index idx_fk_ref_atc2ref_generic cascade;
\set ON_ERROR_STOP 1

create index idx_fk_ref_atc2ref_generic on ref.atc(code, term, fk_data_source);


grant select on ref.atc to group "gm-public";
-- --------------------------------------------------------------
-- .code
comment on column ref.atc.code is
'holds the ATC code';

alter table ref.atc
	alter column code
		set not null;

\unset ON_ERROR_STOP
alter table ref.atc drop constraint ref_atc_uniq_code_per_source cascade;
\set ON_ERROR_STOP 1

alter table ref.atc
	add constraint ref_atc_uniq_code_per_source
		unique(code, fk_data_source);

-- --------------------------------------------------------------
-- .term
comment on column ref.atc.term is
'the name of the drug component';

alter table ref.atc
	alter column term
		set not null;

-- --------------------------------------------------------------
-- .fk_data_source
comment on column ref.atc.fk_data_source is
'foreign key to the exact version of the ATC';

alter table ref.atc
	alter column fk_data_source
		set not null;

\unset ON_ERROR_STOP
alter table ref.atc drop constraint fk_ref_atc2ref_data_source;
\set ON_ERROR_STOP 1

alter table ref.atc
	add foreign key (fk_data_source)
		references ref.data_source(pk)
		on update cascade
		on delete restrict;

\unset ON_ERROR_STOP
drop index idx_fk_ref_atc2ref_data_source cascade;
\set ON_ERROR_STOP 1

create index idx_fk_ref_atc2ref_data_source on ref.atc(fk_data_source);

-- --------------------------------------------------------------
comment on column ref.atc.ddd is
'the Defined Daily Dosage';

-- --------------------------------------------------------------
comment on column ref.atc.unit is
'the unit on the DDD';

-- --------------------------------------------------------------
comment on column ref.atc.administration_route is
'by what route this drug is to be given';

-- --------------------------------------------------------------
-- INSERT/UPDATE sync trigger
\unset ON_ERROR_STOP
drop function ref.trf_ins_upd_sync_atc2generic() cascade;
\set ON_ERROR_STOP 1

create or replace function ref.trf_ins_upd_sync_atc2generic()
	returns trigger
	language 'plpgsql'
	as '
BEGIN
	if TG_OP = ''INSERT'' then
		perform 1 from ref.generic_coding_system where
			code = NEW.code
				and
			term = NEW.term
				and
			fk_data_source = NEW.fk_data_source
		;
		if FOUND then
			return NEW;
		end if;

		insert into ref.generic_coding_system (
			code,
			term,
			fk_data_source
		) values (
			NEW.code,
			NEW.term,
			NEW.fk_data_source
		);

		return NEW;
	end if;

	update ref.generic_coding_system set
		code = NEW.code,
		term = NEW.term,
		fk_data_source = NEW.fk_data_source
	where
		code = OLD.code
			and
		term = OLD.term
			and
		fk_data_source = OLD.fk_data_source
	;

	return NEW;
END;';

comment on function ref.trf_ins_upd_sync_atc2generic() is
	'Sync INSERTs/UPDATEs on ref.atc into ref.generic_coding_system.';

create trigger tr_ins_upd_sync_atc2generic
	before insert or update on ref.atc
		for each row execute procedure ref.trf_ins_upd_sync_atc2generic();

-- --------------------------------------------------------------
-- DELETE sync trigger
\unset ON_ERROR_STOP
drop function ref.trf_del_sync_atc2generic() cascade;
\set ON_ERROR_STOP 1

create or replace function ref.trf_del_sync_atc2generic()
	returns trigger
	language 'plpgsql'
	as '
BEGIN
	delete from ref.generic_coding_system where
		code = OLD.code
			and
		term = OLD.term
			and
		fk_data_source = OLD.fk_data_source
	;
	return OLD;
END;';

comment on function ref.trf_del_sync_atc2generic() is
	'Sync DELETEs on ref.atc into ref.generic_coding_system.';

create trigger tr_del_sync_atc2generic
	after delete on ref.atc
		for each row execute procedure ref.trf_del_sync_atc2generic();

-- --------------------------------------------------------------
-- transfer data from ref.atc_inherited
insert into ref.atc (
	code,
	term,
	fk_data_source,
	ddd,
	unit,
	administration_route
)	select distinct on (code, term, fk_data_source)
		code,
		term,
		fk_data_source,
		ddd,
		unit,
		administration_route
	from
		ref.atc_inherited source
	where not exists (
		select 1 from ref.atc target where
			target.code = source.code
				and
			target.term = source.term
				and
			target.fk_data_source = source.fk_data_source
	);


drop table if exists ref.atc_inherited cascade;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view ref.v_atc cascade;
\set ON_ERROR_STOP 1

create view ref.v_atc as
select
	r_a.pk as pk_atc,
	r_a.code as atc,
	r_a.term,
	r_a.ddd,
	r_a.unit,
	r_a.administration_route,
--	r_a.comment,
	(octet_length(r_a.code) < 7)
		as is_group_code,
	(octet_length(r_a.code) - (octet_length(r_a.code) / 3))
		as atc_level,

	r_ds.name_long,
	r_ds.name_short,
	r_ds.version,
	r_ds.lang,

	r_a.fk_data_source
		as pk_data_source
from
	ref.atc r_a
		inner join ref.data_source r_ds on r_ds.pk = r_a.fk_data_source
;

-- --------------------------------------------------------------
grant select on ref.v_atc to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-ref-atc-dynamic.sql', 'Revision: 1');

-- ==============================================================
