-- project: GNUMed

-- purpose: views for easier clinical data access
-- author: Karsten Hilbert
-- license: GPL (details at http://gnu.org)

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmClinicalViews.sql,v $
-- $Id: gmClinicalViews.sql,v 1.1 2003-04-28 20:40:48 ncq Exp $

-- ===================================================================
-- do fixed string i18n()ing
\i gmI18N.sql

-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ==========================================================
\unset ON_ERROR_STOP
drop view v_allergy;
\set ON_ERROR_STOP 1

create view v_allergy as
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
-- do simple schema revision tracking
\i gmSchemaRevision.sql
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmClinicalViews.sql,v $', '$Revision: 1.1 $');

-- =============================================
-- $Log: gmClinicalViews.sql,v $
-- Revision 1.1  2003-04-28 20:40:48  ncq
-- - this can safely be dropped and recreated even with data in the tables
--
