-- project: GNUMed

-- purpose: views for easier clinical data access
-- author: Karsten Hilbert
-- license: GPL (details at http://gnu.org)

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmClinicalViews.sql,v $
-- $Id: gmClinicalViews.sql,v 1.3 2003-04-29 12:34:54 ncq Exp $

-- ===================================================================
-- do fixed string i18n()ing
\i gmI18N.sql

-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ==========================================================
\unset ON_ERROR_STOP
drop view v_i18n_allergy;
\set ON_ERROR_STOP 1

create view v_i18n_allergy as
select
	a.id as id,
	cn.id_patient as id_patient,
	a.id_clin_transaction as id_clin_transaction,
	a.substance as substance,
	a.id_substance as id_substance,
	a.generics as generics,
	a.allergene as allergene,
	a.atc_code as atc_code,
	a.reaction as reaction,
	a.generic_specific as generic_specific,
	a.definate as definate,
	a.had_hypo as had_hypo,
	_(at.value) as type,
	cn.value as "comment"
from
	allergy a, _enum_allergy_type at, clin_narrative cn
where
	cn.src_table='allergy'
		and
	cn.id=a.id_comment
--		and
--	a.id_type=at.id
;

-- =============================================
\unset ON_ERROR_STOP
drop view v_patient_episodes;
\set ON_ERROR_STOP 1

create view v_patient_episodes as
select
	chi.id_patient as id_patient,
	cep.id as id_episode
from
	clin_health_issue chi, clin_episode cep
where
	cep.id_health_issue = chi.id
;

-- =============================================
\unset ON_ERROR_STOP
drop view v_patient_transactions;
\set ON_ERROR_STOP 1

create view v_patient_transactions as
select
	vpep.id_patient as id_patient,
	tx.id as id_transaction
from
	clin_transaction tx, v_patient_episodes vpep
where
	vpep.id_episode = tx.id_episode
;

-- =============================================
GRANT SELECT ON
	"v_i18n_allergy",
	"v_patient_episodes",
	"v_patient_transactions"
TO GROUP "gm-doctors";

GRANT SELECT, INSERT, UPDATE, DELETE ON
	"v_i18n_allergy",
	"v_patient_episodes",
	"v_patient_transactions"
TO GROUP "_gm-doctors";

-- =============================================
-- do simple schema revision tracking
\i gmSchemaRevision.sql
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmClinicalViews.sql,v $', '$Revision: 1.3 $');

-- =============================================
-- $Log: gmClinicalViews.sql,v $
-- Revision 1.3  2003-04-29 12:34:54  ncq
-- - added more views + grants
--
-- Revision 1.2  2003/04/28 21:39:49  ncq
-- - cleanups and GRANTs
--
-- Revision 1.1  2003/04/28 20:40:48  ncq
-- - this can safely be dropped and recreated even with data in the tables
--
