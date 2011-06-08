-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_episodes_journal cascade;
\set ON_ERROR_STOP 1


create view clin.v_pat_episodes_journal as
select
	cenc.fk_patient
		as pk_patient,
	cep.modified_when
		as modified_when,
	cenc.started
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = cep.modified_by),
		'<' || cep.modified_by || '>'
	)
		as modified_by,
	'a'::text
		as soap_cat,
	_('Episode') || ' ('
		|| case when cep.is_open
			then _('open')
			else _('closed')
			end
		|| coalesce((', ' || cep.diagnostic_certainty_classification), '')
		|| '): '
		|| cep.description || ';'
		|| coalesce((E'\n' || cep.summary || ';'), '')
		|| coalesce ((
				E'\n' || array_to_string (
					(select array_agg(r_csr.code || ' (' || r_ds.name_short || ' - ' || r_ds.version || ' - ' || r_ds.lang || '): ' || r_csr.term)
					 from
					 	clin.lnk_code2episode c_lc2e
					 		inner join
						ref.coding_system_root r_csr on c_lc2e.fk_generic_code = r_csr.pk_coding_system
							inner join
						ref.data_source r_ds on r_ds.pk = r_csr.fk_data_source
					where
						c_lc2e.fk_item = cep.pk
					),
					'; '
				) || ';'
			),
			''
		)
		as narrative,
	cep.fk_encounter
		as pk_encounter,
	cep.pk
		as pk_episode,
	cep.fk_health_issue
		as pk_health_issue,
	cep.pk
		as src_pk,
	'clin.episode'::text
		as src_table,
	cep.row_version
from
	clin.episode cep
		inner join clin.encounter cenc on cep.fk_encounter = cenc.pk
;


grant select on clin.v_pat_episodes_journal TO GROUP "gm-doctors";


select i18n.upd_tx('de', 'open', 'andauernd');
select i18n.upd_tx('de', 'closed', 'abgeschlossen');

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-clin-v_pat_episodes_journal.sql', 'v16');

-- ==============================================================
