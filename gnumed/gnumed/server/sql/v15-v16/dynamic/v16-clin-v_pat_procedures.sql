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
drop view clin.v_pat_procedures cascade;
\set ON_ERROR_STOP 1



create view clin.v_pat_procedures as

select
	cpr.pk
		as pk_procedure,
	cenc.fk_patient
		as pk_patient,
	cpr.soap_cat,
	cpr.clin_when,
	cpr.clin_end,
	cpr.is_ongoing,
	cpr.narrative
		as performed_procedure,
	case
		when cpr.fk_hospital_stay is null then cpr.clin_where
		else chs.narrative
	end
		as clin_where,
	cep.description
		as episode,
	chi.description
		as health_issue,
	cpr.modified_when
		as modified_when,
	coalesce (
		(select short_alias from dem.staff where db_user = cpr.modified_by),
		'<' || cpr.modified_by || '>'
	)
		as modified_by,
	cpr.row_version,
	cpr.fk_encounter
		as pk_encounter,
	cpr.fk_episode
		as pk_episode,
	cpr.fk_hospital_stay
		as pk_hospital_stay,
	cep.fk_health_issue
		as pk_health_issue,
	coalesce (
		(select array_agg(c_lc2p.fk_generic_code) from clin.lnk_code2procedure c_lc2p where c_lc2p.fk_item = cpr.pk),
		ARRAY[]::integer[]
	)
		as pk_generic_codes,
	cpr.xmin as xmin_procedure
from
	clin.procedure cpr
		inner join clin.encounter cenc on cpr.fk_encounter = cenc.pk
			inner join clin.episode cep on cpr.fk_episode = cep.pk
				left join clin.health_issue chi on cep.fk_health_issue = chi.pk
					left join clin.hospital_stay chs on cpr.fk_hospital_stay = chs.pk
;



grant select on clin.v_pat_procedures TO GROUP "gm-doctors";

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_procedures_journal cascade;
\set ON_ERROR_STOP 1


create view clin.v_pat_procedures_journal as
select
	cenc.fk_patient
		as pk_patient,
	cpr.modified_when
		as modified_when,
	cpr.clin_when
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = cpr.modified_by),
		'<' || cpr.modified_by || '>'
	)
		as modified_by,
	cpr.soap_cat
		as soap_cat,
	_('Procedure') || ' "' || cpr.narrative	|| '"'
		|| ' ('
			|| case
				when cpr.fk_hospital_stay is null then cpr.clin_where
				else chs.narrative
			end
			|| coalesce (
				(', ' || _('until') || ' ' || to_char(cpr.clin_end, 'YYYY Mon DD')),
				case
					when (cpr.is_ongoing is True)
						then ', ' || _('ongoing')
						else ''
				end
			)
		|| E')'
		|| coalesce ((
				E'\n' || array_to_string (
					(select array_agg(r_csr.code || ' (' || r_ds.name_short || ' - ' || r_ds.version || ' - ' || r_ds.lang || '): ' || r_csr.term)
					 from
					 	clin.lnk_code2procedure c_lc2p
					 		inner join
						ref.coding_system_root r_csr on c_lc2p.fk_generic_code = r_csr.pk_coding_system
							inner join
						ref.data_source r_ds on r_ds.pk = r_csr.fk_data_source
					where
						c_lc2p.fk_item = cpr.pk
					),
					'; '
				) || ';'
			),
			''
		)
		as narrative,
	cpr.fk_encounter
		as pk_encounter,
	cpr.fk_episode
		as pk_episode,
	cep.fk_health_issue
		as pk_health_issue,
	cpr.pk
		as src_pk,
	'clin.procedure'::text
		as src_table,
	cpr.row_version
from
	clin.procedure cpr
		inner join clin.encounter cenc on cpr.fk_encounter = cenc.pk
			inner join clin.episode cep on cpr.fk_episode = cep.pk
				left join clin.hospital_stay chs on cpr.fk_hospital_stay = chs.pk
;


grant select on clin.v_pat_procedures_journal TO GROUP "gm-doctors";


select i18n.upd_tx('de', 'Procedure', 'Maßnahme');
select i18n.upd_tx('de', 'until', 'bis');
select i18n.upd_tx('de', 'ongoing', 'andauernd');

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-v_pat_procedures.sql', 'v16');

-- ==============================================================
