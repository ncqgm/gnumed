-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view clin.v_pat_substance_intake_journal cascade;
\set ON_ERROR_STOP 1

create view clin.v_pat_substance_intake_journal as


-- brands
select
	(select fk_patient from clin.encounter where pk = c_si.fk_encounter)
		as pk_patient,
	c_si.modified_when
		as modified_when,
	c_si.clin_when
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = c_si.modified_by),
		'<' || c_si.modified_by || '>'
	)
		as modified_by,
	c_si.soap_cat
		as soap_cat,

	(case
		when is_long_term is true then _('long-term') || ' '
		else ''
	 end
	)
		|| _('substance intake') || ' '
		|| (case
				when intake_is_approved_of is true then _('(approved of)')
				when intake_is_approved_of is false then _('(not approved of)')
				else _('(of unknown approval)')
			end)
		|| E':\n'

		|| ' ' || r_cs.description								-- Metoprolol
		|| coalesce(' [' || r_cs.atc_code || '] ', ' ')			-- [ATC]
		|| r_cs.amount::text									-- 100
		|| r_cs.unit || ' '										-- mg
		|| r_bd.preparation										-- tab
		|| coalesce(' ' || c_si.schedule, '')					-- 1-0-0
		|| ', ' || to_char(c_si.clin_when, 'YYYY-MM-DD')		-- 2009-03-01
		|| coalesce(' -> ' || c_si.duration, '')				-- -> 6 months
		|| E'\n'

		|| coalesce (
				' ' || _('discontinued') || to_char(c_si.discontinued, ': YYYY-MM-DD')
				|| coalesce('(' || c_si.discontinue_reason || ')', '')
				|| E'\n',
				''
			)

		|| coalesce (
			nullif (
				(coalesce(' ' || c_si.aim, '')						-- lower RR
				 || coalesce(' (' || c_si.narrative || ')', '')		-- report if unwell
				 || E'\n'
				),
				E'\n'
			),
			''
		)

		|| coalesce (' "' || r_bd.description || '"'													-- "MetoPharm"
			|| coalesce(' [' || r_bd.atc_code || ']', '')												-- [ATC code]
			|| coalesce(' (' || r_bd.external_code_type || ': ' || r_bd.external_code || ')', ''),		-- (external code)
			'')

	as narrative,

	c_si.fk_encounter
		as pk_encounter,
	c_si.fk_episode
		as pk_episode,
	(select fk_health_issue from clin.episode where pk = c_si.fk_episode)
		as pk_health_issue,
	c_si.pk
		as src_pk,
	'clin.substance_intake'::text
		as src_table,
	c_si.row_version
		as row_version
from
	clin.substance_intake c_si
		inner join ref.lnk_substance2brand r_ls2b on (c_si.fk_drug_component = r_ls2b.pk)
			inner join ref.branded_drug r_bd on (r_bd.pk = r_ls2b.fk_brand)
			inner join ref.consumable_substance r_cs on (r_cs.pk = r_ls2b.fk_substance)
where
	c_si.fk_drug_component is not null


			union all


-- substances w/o brands
select
	(select fk_patient from clin.encounter where pk = c_si.fk_encounter)
		as pk_patient,
	c_si.modified_when
		as modified_when,
	c_si.clin_when
		as clin_when,
	coalesce (
		(select short_alias from dem.staff where db_user = c_si.modified_by),
		'<' || c_si.modified_by || '>'
	)
		as modified_by,
	c_si.soap_cat
		as soap_cat,

	(case
		when is_long_term is true then _('long-term') || ' '
		else ''
	 end
	)
		|| _('substance intake') || ' '
		|| (case
				when intake_is_approved_of is true then _('(approved of)')
				when intake_is_approved_of is false then _('(not approved of)')
				else _('(of unknown approval)')
			end)
		|| E':\n'

		|| ' ' || r_cs.description								-- Metoprolol
		|| coalesce(' [' || r_cs.atc_code || '] ', ' ')			-- [ATC]
		|| r_cs.amount || r_cs.unit || ' '						-- 100mg
		|| c_si.preparation										-- tab
		|| coalesce(' ' || c_si.schedule, '')					-- 1-0-0
		|| ', ' || to_char(c_si.clin_when, 'YYYY-MM-DD')		-- 2009-03-01
		|| coalesce(' -> ' || c_si.duration, '')				-- -> 6 months
		|| E'\n'

		|| coalesce (
				' ' || _('discontinued') || to_char(c_si.discontinued, ': YYYY-MM-DD')
				|| coalesce('(' || c_si.discontinue_reason || ')', '')
				|| E'\n',
				''
			)

		|| coalesce (
			nullif (
				(coalesce(' ' || c_si.aim, '')						-- lower RR
				 || coalesce(' (' || c_si.narrative || ')', '')		-- report if unwell
				 || E'\n'
				),
				E'\n'
			),
			''
		)
	as narrative,

	c_si.fk_encounter
		as pk_encounter,
	c_si.fk_episode
		as pk_episode,
	(select fk_health_issue from clin.episode where pk = c_si.fk_episode)
		as pk_health_issue,
	c_si.pk
		as src_pk,
	'clin.substance_intake'::text
		as src_table,
	c_si.row_version
		as row_version
from
	clin.substance_intake c_si
		inner join ref.consumable_substance r_cs on (r_cs.pk = c_si.fk_substance)
where
	c_si.fk_drug_component is null

;


grant select on clin.v_pat_substance_intake_journal to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v13-clin-substance_intake-dynamic.sql,v $', '$Revision: 1.8 $');

-- ==============================================================
