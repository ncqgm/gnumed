-- project: GNUMed

-- purpose: views for easier clinical data access
-- author: Karsten Hilbert
-- license: GPL (details at http://gnu.org)

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmClinicalViews.sql,v $
-- $Id: gmClinicalViews.sql,v 1.7 2003-05-03 00:44:05 ncq Exp $

-- ===================================================================
-- do fixed string i18n()ing
\i gmI18N.sql

-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

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

-- ==========================================================
-- allergy stuff
\unset ON_ERROR_STOP
drop trigger t_allergy_add_del on allergy;
drop function f_announce_allergy_add_del();
\set ON_ERROR_STOP 1

create function f_announce_allergy_add_del() returns opaque as '
begin
	notify "allergy_add_del_db";
	return NEW;
end;
' language 'plpgsql';

create trigger t_allergy_add_del
	after insert or delete on allergy
	for each row execute procedure f_announce_allergy_add_del()
;
-- should really be "for each statement" but that isn't supported yet

\unset ON_ERROR_STOP
drop view v_i18n_patient_allergies;
\set ON_ERROR_STOP 1

create view v_i18n_patient_allergies as
select
	a.id as id,
	vpt.id_patient as id_patient,
	a.id_clin_transaction as id_clin_transaction,
	a.substance as substance,
	a.substance_code as substance_code,
	a.generics as generics,
	a.allergene as allergene,
	a.atc_code as atc_code,
	a.reaction as reaction,
	a.generic_specific as generic_specific,
	a.definate as definate,
	_(at.value) as type,
	cn.value as "comment"
from
	(allergy a left outer join clin_narrative cn on (a.id_comment=cn.id)), _enum_allergy_type at, v_patient_transactions vpt
where
	vpt.id_transaction=a.id_clin_transaction
		and
	at.id=a.id_type
;

-- =============================================
GRANT SELECT ON
	"v_patient_episodes",
	"v_patient_transactions",
	"v_i18n_patient_allergies"
TO GROUP "gm-doctors";

GRANT SELECT, INSERT, UPDATE, DELETE ON
	"v_patient_episodes",
	"v_patient_transactions",
	"v_i18n_patient_allergies"
TO GROUP "_gm-doctors";

-- =============================================
-- do simple schema revision tracking
\i gmSchemaRevision.sql
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmClinicalViews.sql,v $', '$Revision: 1.7 $');

-- =============================================
-- $Log: gmClinicalViews.sql,v $
-- Revision 1.7  2003-05-03 00:44:05  ncq
-- - make patient allergies view work
--
-- Revision 1.6  2003/05/02 15:06:19  ncq
-- - make trigger return happy
-- - tweak v_i18n_patient_allergies - not done yet
--
-- Revision 1.5  2003/05/01 15:05:36  ncq
-- - function/trigger to announce insertion/deletion of allergy
-- - allergy.id_substance -> allergy.substance_code
--
-- Revision 1.4  2003/04/30 23:30:29  ncq
-- - v_i18n_patient_allergies
-- - new_allergy -> allergy_new
--
-- Revision 1.3  2003/04/29 12:34:54  ncq
-- - added more views + grants
--
-- Revision 1.2  2003/04/28 21:39:49  ncq
-- - cleanups and GRANTs
--
-- Revision 1.1  2003/04/28 20:40:48  ncq
-- - this can safely be dropped and recreated even with data in the tables
--
