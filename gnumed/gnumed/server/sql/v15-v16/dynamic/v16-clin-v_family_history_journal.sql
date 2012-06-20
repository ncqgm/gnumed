-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_hx_family_journal cascade;
drop view clin.v_family_history_journal cascade;
\set ON_ERROR_STOP 1


create view clin.v_family_history_journal as
select
	cenc.fk_patient
		as pk_patient,
	c_fh.modified_when
		as modified_when,
	c_fh.clin_when
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = c_fh.modified_by),
		'<' || c_fh.modified_by || '>'
	)
		as modified_by,
	c_fh.soap_cat
		as soap_cat,
	_(c_fhrt.description)
			|| coalesce(' @ ' || c_fh.age_noted, '')
			|| ': '
			|| c_fh.narrative
			|| E'\n'
			|| ' '
			|| case
				when c_fh.contributed_to_death is True
					then _('contributed to death') || ' '
				else ''
			end
			|| coalesce('@ ' || justify_interval(c_fh.age_of_death)::text, '')
			|| E'\n'
			|| coalesce(' ' || c_fh.name_relative || ',', '')
			|| coalesce(' ' || to_char(c_fh.dob_relative, 'YYYY-MM-DD'), '')
			|| coalesce(E'\n ' || c_fh.comment, '')
			|| coalesce ((
					E';\n' || array_to_string (
						(select array_agg(r_csr.code || ' (' || r_ds.name_short || ' - ' || r_ds.version || ' - ' || r_ds.lang || '): ' || r_csr.term)
						 from
						 	clin.lnk_code2fhx c_lc2fhx
						 		inner join
							ref.coding_system_root r_csr on c_lc2fhx.fk_generic_code = r_csr.pk_coding_system
								inner join
							ref.data_source r_ds on r_ds.pk = r_csr.fk_data_source
						where
							c_lc2fhx.fk_item = c_fh.pk
						),
						'; '
					) || ';'
				),
				''
			)
		as narrative,
	c_fh.fk_encounter
		as pk_encounter,
	c_fh.fk_episode
		as pk_episode,
	cep.fk_health_issue
		as pk_health_issue,
	c_fh.pk
		as src_pk,
	'clin.family_history'::text
		as src_table,
	c_fh.row_version
from
	clin.family_history c_fh
		inner join clin.encounter cenc on c_fh.fk_encounter = cenc.pk
			inner join clin.episode cep on c_fh.fk_episode = cep.pk
				left join clin.fhx_relation_type c_fhrt on c_fh.fk_relation_type = c_fhrt.pk
;


grant select on clin.v_family_history_journal to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-v_family_history_journal.sql', 'v16.0');

-- ==============================================================
