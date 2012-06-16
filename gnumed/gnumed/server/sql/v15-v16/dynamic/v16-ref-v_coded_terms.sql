-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;
--set check_function_bodies to on;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view ref.v_coded_terms cascade;
\set ON_ERROR_STOP 1



create view ref.v_coded_terms as

	select
		r_csr.code,
		r_csr.term,
		r_ds.name_short
			as coding_system,
		r_ds.name_long
			as coding_system_long,
		r_ds.version,
		r_ds.lang,
		r_csr.pk_coding_system
			as pk_generic_code
	from
		ref.coding_system_root r_csr
			inner join ref.data_source r_ds on r_csr.fk_data_source = r_ds.pk

UNION

	select
		ri.code,
		r_it.synonym
			as term,
		r_ds.name_short
			as coding_system,
		r_ds.name_long
			as coding_system_long,
		r_ds.version,
		r_ds.lang,
		r_it.fk_code
			as pk_generic_code
	from
		ref.icpc_thesaurus r_it
			left join ref.icpc ri on (r_it.fk_code = ri.pk_coding_system)
				left join ref.data_source r_ds on (ri.fk_data_source = r_ds.pk)
	;

;



grant select on ref.v_coded_terms to group "gm-public";



comment on view ref.v_coded_terms is
'This view aggregates all official (reference) terms, including "official" synonyms, for which a corresponding code is known to the system.';

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-ref-v_coded_terms.sql', 'v16');

-- ==============================================================
