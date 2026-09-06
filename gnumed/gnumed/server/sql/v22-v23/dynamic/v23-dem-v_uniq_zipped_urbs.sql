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
CREATE OR REPLACE VIEW dem.v_uniq_zipped_urbs AS
	-- all the cities that
	SELECT
		d_u.postcode,
		d_u.name,
		d_r.name AS region,
		d_r.code AS code_region,
		d_c.name AS country,
		COALESCE(tx_exact_lang.trans, tx_reduced_lang.trans, d_c.name)
			AS l10n_country,
		d_r.country AS code_country
	FROM
		dem.urb d_u,
		dem.region d_r,
		dem.country d_c
			LEFT JOIN i18n.translations tx_exact_lang ON
				tx_exact_lang.orig = d_c.name
					AND
				tx_exact_lang.lang = (SELECT lang FROM i18n.curr_lang WHERE db_user = current_user)
			LEFT JOIN i18n.translations tx_reduced_lang ON
				tx_reduced_lang.orig = d_c.name
					AND
				tx_reduced_lang.lang = (SELECT regexp_replace(lang, '_.*$', '') FROM i18n.curr_lang WHERE db_user = current_user)
	WHERE
		-- have a zip code
		d_u.postcode IS NOT NULL
			AND
		-- are not found in dem.street with this zip code
		NOT EXISTS (
			SELECT 1 FROM
				dem.street d_str2
					JOIN dem.urb d_u2 ON d_str2.id_urb = d_u2.id
			WHERE
				d_str2.postcode IS NOT NULL
					AND
				d_str2.postcode = d_u.postcode
					AND
				d_u2.name = d_u.name
		)
			AND
		d_u.fk_region = d_r.pk
			AND
		d_r.country = d_c.code
;

comment on view dem.v_uniq_zipped_urbs is
'convenience view that selects urbs which:
- have a zip code
- are not referenced in table dem.street with that zip code';

grant select on dem.v_uniq_zipped_urbs to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-dem-v_uniq_zipped_urbs.sql', '23.0');
