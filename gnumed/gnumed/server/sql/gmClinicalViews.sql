-- project: GnuMed

-- purpose: views for easier clinical data access
-- author: Karsten Hilbert
-- license: GPL (details at http://gnu.org)

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmClinicalViews.sql,v $
-- $Id: gmClinicalViews.sql,v 1.9 2003-05-05 00:19:12 ncq Exp $

-- ===================================================================
-- do fixed string i18n()ing
\i gmI18N.sql

-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================
\unset ON_ERROR_STOP
drop index idx_item_encounter;
drop index idx_item_episode;
drop index idx_narrative_patient;
drop index idx_narrative_src_table;
drop index idx_episode_h_issue;
drop index idx_allergy_comment;
\set ON_ERROR_STOP 1

create index idx_item_encounter on clin_item(id_encounter);
create index idx_item_episode on clin_item(id_episode);
create index idx_narrative_patient on clin_narrative(id_patient);
create index idx_narrative_src_table on clin_narrative(src_table);
create index idx_episode_h_issue on clin_episode(id_health_issue);
create index idx_allergy_comment on allergy(id_comment);

-- =============================================
\unset ON_ERROR_STOP
drop view v_i18n_enum_encounter_type;
\set ON_ERROR_STOP 1

create view v_i18n_enum_encounter_type as
select
	_enum_encounter_type.id,
	_(_enum_encounter_type.description)
from
	_enum_encounter_type
;

-- =============================================
\unset ON_ERROR_STOP
drop view v_patient_episodes;
\set ON_ERROR_STOP 1

create view v_patient_episodes as
select
	chi.id_patient as id_patient,
	cep.id as id_episode,
	chi.id as id_health_issue,
	cep.description as episode,
	cn.value as episode_comment,
	chi.description as health_issue
from
	(clin_episode cep left outer join clin_narrative cn on (cep.id_comment=cn.id)), clin_health_issue chi
where
	cep.id_health_issue=chi.id
;

-- =============================================
\unset ON_ERROR_STOP
drop view v_patient_items;
\set ON_ERROR_STOP 1

create view v_patient_items as
select
	ci.item_pkey as item_pkey,
	ci.id_encounter as id_encounter,
	ci.id_episode as id_episode,
	vpep.id_patient as id_patient,
	vpep.id_health_issue as id_health_issue,
	pgc.relname as src_table
from
	clin_item ci, v_patient_episodes vpep, pg_class pgc
where
	vpep.id_episode=ci.id_episode
		and
	ci.tableoid=pgc.oid
;

-- =============================================
\unset ON_ERROR_STOP
drop view v_i18n_patient_encounters;
\set ON_ERROR_STOP 1

create view v_i18n_patient_encounters as
select distinct on (vpi.id_encounter)
	ce.id as id_encounter,
	ce.id_location as id_location,
	ce.id_provider as id_provider,
	vpi.id_patient as id_patient,
	_(et.description) as type,
	cn.value as "comment"
from
	(clin_encounter ce left outer join clin_narrative cn on (ce.id_comment=cn.id)),
	(clin_encounter inner join v_patient_items vpi on (clin_encounter.id=vpi.id_encounter)),
	_enum_encounter_type et
where
--	vpi.id_encounter=ce.id
--		and
	et.id=ce.id_type
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
-- should really be "for each statement" but that isn't supported yet by PostgreSQL

\unset ON_ERROR_STOP
drop view v_i18n_patient_allergies;
\set ON_ERROR_STOP 1

create view v_i18n_patient_allergies as
select
	a.id as id,
	a.item_pkey as item_pkey,
	vpep.id_patient as id_patient,
	vpep.id_health_issue as id_health_issue,
	a.id_episode as id_episode,
	a.id_encounter as id_encounter,
	a.substance as substance,
	a.substance_code as substance_code,
	a.generics as generics,
	a.allergene as allergene,
	a.atc_code as atc_code,
	a.reaction as reaction,
	a.generic_specific as generic_specific,
	a.definate as definate,
	a.id_type as id_type,
	_(at.value) as type,
	cn.value as "comment"
from
	(allergy a left outer join clin_narrative cn on (a.id_comment=cn.id)), _enum_allergy_type at, v_patient_episodes vpep
where
	vpep.id_episode=a.id_episode
		and
	at.id=a.id_type
;

-- =============================================
GRANT SELECT ON
	"v_patient_episodes",
	"v_patient_items",
	"v_i18n_patient_encounters",
	"v_i18n_patient_allergies"
TO GROUP "gm-doctors";

GRANT SELECT, INSERT, UPDATE, DELETE ON
	"v_patient_episodes",
	"v_patient_items",
	"v_i18n_patient_encounters",
	"v_i18n_patient_allergies"
TO GROUP "_gm-doctors";

-- =============================================
-- do simple schema revision tracking
\i gmSchemaRevision.sql

\unset ON_ERROR_STOP
delete from gm_schema_revision where filename='$RCSfile: gmClinicalViews.sql,v $';
\set ON_ERROR_STOP 1

INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmClinicalViews.sql,v $', '$Revision: 1.9 $');

-- =============================================
-- $Log: gmClinicalViews.sql,v $
-- Revision 1.9  2003-05-05 00:19:12  ncq
-- - we do need the v_i18n_ on encounter types
--
-- Revision 1.8  2003/05/04 23:35:59  ncq
-- - major reworking to follow the formal EMR structure writeup
--
-- Revision 1.7  2003/05/03 00:44:05  ncq
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
