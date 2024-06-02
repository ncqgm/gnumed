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
-- data transfer
-- --------------------------------------------------------------
drop function if exists staging.v22_v23_transfer_intakes() cascade;

create function staging.v22_v23_transfer_intakes()
	returns void
	language plpgsql
	as '
DECLARE
	_rec record;
	_pk_clin_intake integer;
BEGIN
	FOR _rec IN (SELECT * FROM clin.v_substance_intakes) LOOP
		-- intake exists ?
		SELECT pk INTO _pk_clin_intake FROM clin.intake WHERE
			clin.map_enc_or_epi_to_patient(fk_encounter, fk_episode) = _rec.pk_patient
				AND
			fk_substance = _rec.pk_substance
		;
		IF NOT FOUND THEN
			-- create new row in clin.intake
			INSERT INTO clin.intake (
				fk_encounter,
				fk_episode,
				clin_when,
				fk_substance,
				_fk_s_i
			) VALUES (
				_rec.pk_encounter,
				_rec.pk_episode,
				coalesce(_rec.started, now()),
				_rec.pk_substance,
				_rec.pk_substance_intake
			) RETURNING pk INTO _pk_clin_intake;
		END IF;
		-- update aggregate fields
		UPDATE clin.intake SET
			narrative = nullif(coalesce(narrative, '''') || coalesce(E''\n'' || _rec.notes, ''''), ''''),
			notes4patient = nullif(coalesce(notes4patient, '''') || coalesce(E''\n'' || _rec.aim, ''''), '''')
		WHERE
			pk = _pk_clin_intake;
	END LOOP;
	-- set use type on better-safe-than-sorry policy:
	-- medication ?
	UPDATE clin.intake SET
		use_type = NULL::integer
	WHERE EXISTS (
		SELECT 1 FROM clin.v_substance_intakes c_vsi
		WHERE
			c_vsi.pk_patient = clin.map_enc_or_epi_to_patient(fk_encounter, fk_episode)
				AND
			c_vsi.pk_substance = fk_substance
				AND
			c_vsi.harmful_use_type IS NULL
	);
	-- or non-harmful use ?
	UPDATE clin.intake SET
		use_type = 0
	WHERE EXISTS (
		SELECT 1 FROM clin.v_substance_intakes c_vsi
		WHERE
			c_vsi.pk_patient = clin.map_enc_or_epi_to_patient(fk_encounter, fk_episode)
				AND
			c_vsi.pk_substance = fk_substance
				AND
			c_vsi.harmful_use_type = 0
	);
	-- or previous addiction ?
	UPDATE clin.intake SET
		use_type = 3
	WHERE EXISTS (
		SELECT 1 FROM clin.v_substance_intakes c_vsi
		WHERE
			c_vsi.pk_patient = clin.map_enc_or_epi_to_patient(fk_encounter, fk_episode)
				AND
			c_vsi.pk_substance = fk_substance
				AND
			c_vsi.harmful_use_type = 3
	);
	-- or currently harmful use ?
	UPDATE clin.intake SET
		use_type = 1
	WHERE EXISTS (
		SELECT 1 FROM clin.v_substance_intakes c_vsi
		WHERE
			c_vsi.pk_patient = clin.map_enc_or_epi_to_patient(fk_encounter, fk_episode)
				AND
			c_vsi.pk_substance = fk_substance
				AND
			c_vsi.harmful_use_type = 1
	);
	-- or currently addicted ?
	UPDATE clin.intake SET
		use_type = 2
	WHERE EXISTS (
		SELECT 1 FROM clin.v_substance_intakes c_vsi
		WHERE
			c_vsi.pk_patient = clin.map_enc_or_epi_to_patient(fk_encounter, fk_episode)
				AND
			c_vsi.pk_substance = fk_substance
				AND
			c_vsi.harmful_use_type = 2
	);
END;';

comment on function staging.v22_v23_transfer_intakes() is 'Temporary function to transfer from clin.substance_intake to clin.intake.';

-- transfer intake data
select staging.v22_v23_transfer_intakes();

drop function if exists staging.v22_v23_transfer_intakes() cascade;

-- --------------------------------------------------------------
-- transfer regimen data
insert into clin.intake_regimen (
	fk_intake,
	amount,
	unit,
	clin_when,
	comment_on_start,
	discontinued,
	discontinue_reason,
	planned_duration,
	narrative,
	fk_encounter,
	fk_episode
)
	select
		c_i.pk,
		(select amount from clin.v_substance_intakes where pk_substance_intake = c_i._fk_s_i),
		(select unit from clin.v_substance_intakes where pk_substance_intake = c_i._fk_s_i),
		c_i.clin_when,
		c_si.comment_on_start,
		c_si.discontinued,
		c_si.discontinue_reason,
		c_si.duration,
		coalesce(c_si.schedule, 'per plan'),
		c_i.fk_encounter,
		c_i.fk_episode
	from
		clin.intake c_i
			inner join clin.substance_intake c_si on (c_si.pk = c_i._fk_s_i)
	where not exists (
		select 1 from clin.intake_regimen where fk_intake = c_i.pk
	)
;

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-intake_regimen-transfer_data.sql', '23.0');
