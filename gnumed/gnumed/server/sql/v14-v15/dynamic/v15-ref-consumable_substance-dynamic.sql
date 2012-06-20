-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
set check_function_bodies to 'on';
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
select audit.add_table_for_audit('ref', 'consumable_substance');
select gm.add_table_for_notifies('ref', 'consumable_substance');



comment on table ref.consumable_substance is
'lists substances that are consumable by patients,
 whether or not linked to a branded drug';

-- --------------------------------------------------------------
-- .description
comment on column ref.consumable_substance.description is
	'The substance name.';

\unset ON_ERROR_STOP
alter table ref.consumable_substance drop constraint ref_subst_sane_desc cascade;
\set ON_ERROR_STOP 1

alter table ref.consumable_substance
	add constraint ref_subst_sane_desc
		check (gm.is_null_or_blank_string(description) is False);

-- --------------------------------------------------------------
-- .atc_code
comment on column ref.consumable_substance.atc_code is
'(One) Anatomic Therapeutic Chemical code for this substance.

Note that substances can have *several* ATC codes assigned
to it by the WHO denoting different therapeutic uses and/or
local application formulations.

This code can *only* be used to *identify* the substance,
not the use/application formulation thereof.';

\unset ON_ERROR_STOP
alter table ref.consumable_substance drop constraint ref_subst_sane_atc cascade;
\set ON_ERROR_STOP 1

alter table ref.consumable_substance
	add constraint ref_subst_sane_atc
		check (gm.is_null_or_non_empty_string(atc_code) is True);

-- --------------------------------------------------------------
-- .amount
comment on column ref.consumable_substance.amount is
	'The amount of substance.';

\unset ON_ERROR_STOP
alter table ref.consumable_substance drop constraint ref_consumable_sane_amount cascade;
\set ON_ERROR_STOP 1

alter table ref.consumable_substance
	alter column amount
		set not null;

alter table ref.consumable_substance
	add constraint ref_consumable_sane_amount
		check (amount > 0);

-- --------------------------------------------------------------
-- .unit
comment on column ref.consumable_substance.unit is
	'The unit of the amount of substance.';

\unset ON_ERROR_STOP
alter table ref.consumable_substance drop constraint ref_consumable_sane_unit cascade;
\set ON_ERROR_STOP 1

alter table ref.consumable_substance
	add constraint ref_consumable_sane_unit
		check (gm.is_null_or_blank_string(unit) is False);

-- --------------------------------------------------------------
-- table constraints
\unset ON_ERROR_STOP
alter table ref.consumable_substance drop constraint ref_consumable_uniq_subst_amount_unit cascade;
\set ON_ERROR_STOP 1

alter table ref.consumable_substance
	add constraint ref_consumable_uniq_subst_amount_unit
		unique(description, amount, unit);


-- --------------------------------------------------------------
-- grants
grant select, insert, update, delete on
	ref.consumable_substance
to group "gm-doctors";

grant select, select, update on
	ref.consumable_substance_pk_seq
to group "gm-doctors";

-- --------------------------------------------------------------
-- sample data
\unset ON_ERROR_STOP
insert into ref.consumable_substance (
	description,
	atc_code,
	amount,
	unit
) values
	('Ibuprofen', 'M01AE01', 600, 'mg'),
	('tobacco', 'N07BA01', 1, 'pack'),
	('nicotine', 'N07BA01', 1, 'pack'),
	('alcohol', 'V03AB16', 1, 'glass'),
	('Tabak', 'N07BA01', 1, 'Schachtel'),
	('Nikotin', 'N07BA01', 1, 'Schachtel'),
	('Alkohol', 'V03AB16', 1, 'Glas'),
	('Nikotin', 'N07BA01', 0.8, 'mg'),
	('Teer', 'D05AA', 10, 'mg'),
	('Kohlenmonoxid', NULL, 10, 'mg')
;
\set ON_ERROR_STOP 1



delete from ref.consumable_substance where description like '%-Starship';

insert into ref.consumable_substance (
	description,
	atc_code,
	amount,
	unit
) values (
	'Ibuprofen-Starship',
	'M01AE01',
	800,
	'mg'
);

-- --------------------------------------------------------------
-- generate clin.consumable_substance entries from v14 database knowledge
\unset ON_ERROR_STOP
drop function tmp_transfer_consumable_substances() cascade;
\set ON_ERROR_STOP 1


create or replace function tmp_transfer_consumable_substances()
	returns boolean
	language 'plpgsql'
	as '
DECLARE
	_prev_record record;
BEGIN

	-- 1) clin.consumed_substance
	raise notice ''creating ref.consumable_substance rows from clin.consumed_substance'';

	for _prev_record in
		SELECT * FROM clin.consumed_substance ccs JOIN clin.substance_intake csi ON (csi.fk_substance = ccs.pk)
	loop

		if _prev_record.tmp_amount is NULL then
			_prev_record.tmp_amount := 99999.3;
		end if;

		if _prev_record.tmp_unit is NULL then
			_prev_record.tmp_amount := ''*?* (clin.consumed_substance)'';
		end if;

		raise notice ''transferring % (% %)'', _prev_record.description, _prev_record.tmp_amount, _prev_record.tmp_unit;

		-- already exists ?
		perform 1 from ref.consumable_substance rcs
		where
			rcs.description = _prev_record.description
				and
			rcs.amount = _prev_record.tmp_amount
				and
			rcs.unit = _prev_record.tmp_unit;

		if found then
			raise notice ''already exists'';
			continue;
		end if;

		insert into ref.consumable_substance (
			description,
			atc_code,
			amount,
			unit
		) values (
			_prev_record.description,
			_prev_record.atc_code,
			_prev_record.tmp_amount,
			_prev_record.tmp_unit
		);

	end loop;


	-- 2) ref.substance_in_brand
	raise notice ''creating ref.consumable_substance rows from ref.substance_in_brand'';

	for _prev_record in
		SELECT * FROM ref.substance_in_brand rsib JOIN clin.substance_intake csi ON (csi.fk_brand = rsib.fk_brand)
	loop

		if _prev_record.tmp_amount is NULL then
			_prev_record.tmp_amount := 99999.4;
		end if;

		if _prev_record.tmp_unit is NULL then
			_prev_record.tmp_amount := ''*?* (ref.substance_in_brand)'';
		end if;

		raise notice ''transferring % (% %)'', _prev_record.description, _prev_record.tmp_amount, _prev_record.tmp_unit;

		-- already exists ?
		perform 1 from ref.consumable_substance rcs
		where
			rcs.description = _prev_record.description
				and
			rcs.amount = _prev_record.tmp_amount
				and
			rcs.unit = _prev_record.tmp_unit;

		if found then
			raise notice ''already exists'';
			continue;
		end if;

		insert into ref.consumable_substance (
			description,
			atc_code,
			amount,
			unit
		) values (
			_prev_record.description,
			_prev_record.atc_code,
			_prev_record.tmp_amount,
			_prev_record.tmp_unit
		);

	end loop;

	return True;
END;';


select tmp_transfer_consumable_substances();


drop function tmp_transfer_consumable_substances() cascade;

-- --------------------------------------------------------------
-- MUST protect from changing if in use directly or indirectly
\unset ON_ERROR_STOP
drop function ref.trf_do_not_update_substance_if_taken_by_patient() cascade;
\set ON_ERROR_STOP 1

create or replace function ref.trf_do_not_update_substance_if_taken_by_patient()
	returns trigger
	language 'plpgsql'
	as '
DECLARE
	_msg text;
BEGIN
	if OLD.description = NEW.description then
		if OLD.amount = NEW.amount then
			if OLD.unit = NEW.unit then
				return NEW;
			end if;
		end if;
	end if;

	_msg := ''[ref.trf_do_not_update_substance_if_taken_by_patient]: as long as substance <'' || OLD.description || ''> is taken by a patient you cannot modify it'';

	perform 1 from clin.substance_intake c_si
	where c_si.fk_substance = OLD.pk
	limit 1;

	if FOUND then
		raise exception ''%'', _msg;
	end if;

	PERFORM 1
	FROM clin.substance_intake c_si
	WHERE c_si.fk_drug_component IN (
		-- get all PKs in component link table which
		-- represent the substance we want to modify
		SELECT
			r_ls2b.pk
		FROM
			ref.lnk_substance2brand r_ls2b
		WHERE
			r_ls2b.fk_substance = OLD.pk
	)
	LIMIT 1;

	if FOUND then
		raise exception ''%'', _msg;
	end if;

	return NEW;
END;';

comment on function ref.trf_do_not_update_substance_if_taken_by_patient() is
'If this substance is taken by any patient do not modify it (description, amount, unit).';

create trigger tr_do_not_update_substance_if_taken_by_patient
	before update
	on ref.consumable_substance
	for each row execute procedure ref.trf_do_not_update_substance_if_taken_by_patient()
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v12-ref-consumable_substance-dynamic.sql', 'Revision: 1.1');

-- ==============================================================
