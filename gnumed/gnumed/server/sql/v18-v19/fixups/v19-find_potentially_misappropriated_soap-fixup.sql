-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
delete from cfg.report_query where label = 'bug: find SOAP entries potentially misappropriated to the wrong episode';

insert into cfg.report_query (label, cmd) values (
	'bug: find SOAP entries potentially misappropriated to the wrong episode',
'-- change ''second'' to ''minute'' or ''hour'' in order to find
-- even more candidates of potential misappropriation
SELECT
	pk_patient,
	pk_episode,
	pk_encounter,
	soap_cat,
	modified_by,
	modified_when,
	narrative
FROM clin.v_emr_journal
WHERE
	(	pk_patient,
		pk_episode,
		pk_encounter,
		soap_cat,
		modified_by,
		date_trunc(''second'', modified_when)
	) IN (
		SELECT
			c_vej.pk_patient,
			c_vej.pk_episode,
			c_vej.pk_encounter,
			c_vej.soap_cat,
			c_vej.modified_by,
			date_trunc(''second'', c_vej.modified_when)
		FROM clin.v_emr_journal c_vej
		WHERE
			c_vej.src_table = ''clin.clin_narrative''
				AND
			c_vej.row_version = 0
		GROUP BY
			c_vej.pk_patient,
			c_vej.pk_episode,
			c_vej.pk_encounter,
			c_vej.soap_cat,
			c_vej.modified_by,
			date_trunc(''second'', c_vej.modified_when)
		HAVING COUNT(*) > 1
	)
ORDER BY
	pk_patient,
	pk_episode,
	pk_encounter,
	soap_cat,
	modified_by,
	modified_when
;');

-- --------------------------------------------------------------
select gm.log_script_insertion('v19-find_potentially_misappropriated_soap-fixup.sql', '19.8');
