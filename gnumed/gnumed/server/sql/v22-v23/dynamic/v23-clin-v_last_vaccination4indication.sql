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
drop view if exists clin.v_pat_last_vacc4indication cascade;
drop view if exists clin.v_last_vaccination4indication cascade;

create view clin.v_last_vaccination4indication as
	SELECT
		c_vv4i.*,
		shots_per_ind.no_of_shots
	FROM
		clin.v_vaccinations4indication c_vv4i
			join (
				SELECT
					COUNT(1) AS no_of_shots,
					pk_patient,
					atc_indication
				FROM clin.v_vaccinations4indication
				GROUP BY
					pk_patient,
					atc_indication
				) AS shots_per_ind
			ON (c_vv4i.pk_patient = shots_per_ind.pk_patient AND c_vv4i.atc_indication = shots_per_ind.atc_indication)
	WHERE
		c_vv4i.date_given = (
			select
				max(c_vv4i_2.date_given)
			from
				clin.v_vaccinations4indication c_vv4i_2
			where
				c_vv4i.pk_patient = c_vv4i_2.pk_patient
					and
				c_vv4i.atc_indication = c_vv4i_2.atc_indication
		)

;

comment on view clin.v_last_vaccination4indication is
	'Lists *latest* vaccinations with total count per indication.';

grant select on clin.v_last_vaccination4indication to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-v_last_vaccination4indication.sql', '23.0');
