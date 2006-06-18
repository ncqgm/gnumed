-- Project: GNUmed
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmDemographics-Grants.sql,v $
-- $Revision: 1.19 $
-- license: GPL
-- authors: Ian Haywood, Horst Herb, Karsten Hilbert, Richard Terry

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- schema
grant usage on schema dem to group "gm-doctors";

grant select on
	dem.name_gender_map
to group "gm-public";

-- do not allow anyone other the gm-dbo to DELETE on identity ...
grant select, insert, update on
	dem.identity,
	dem.identity_pk_seq
to group "gm-doctors";

grant select on
	dem.staff,
	dem.staff_role
to group "gm-doctors";

GRANT SELECT, INSERT, UPDATE, DELETE ON
	dem.names,
	dem.names_id_seq,
	dem.urb,
	dem.urb_id_seq,
	dem.country,
	dem.country_id_seq,
	dem.state,
	dem.state_id_seq,
	dem.street,
	dem.street_id_seq,
	dem.address,
	dem.address_id_seq,
	dem.address_type,
	dem.address_type_id_seq,
	dem.enum_comm_types,
	dem.enum_ext_id_types,
	dem.enum_ext_id_types_pk_seq
	, dem.gender_label
	, dem.gender_label_pk_seq,
	dem.lnk_identity2ext_id,
	dem.lnk_identity2ext_id_id_seq,
	dem.lnk_person_org_address,
	dem.lnk_person_org_address_id_seq,
	dem.lnk_identity2comm,
	dem.lnk_identity2comm_id_seq,
	dem.relation_types,
	dem.lnk_person2relative,
	dem.lnk_person2relative_id_seq,
	dem.occupation,
	dem.occupation_id_seq,	
	dem.lnk_job2person,
	dem.lnk_job2person_id_seq,
	dem.org_category,
	dem.org,
	dem.org_id_seq,
	dem.lnk_org2comm,
	dem.lnk_org2comm_id_seq,
	dem.marital_status
TO GROUP "gm-doctors";

-- ===================================================================
-- $Log: gmDemographics-Grants.sql,v $
-- Revision 1.19  2006-06-18 13:26:12  ncq
-- - we *do* need select on dem.staff (so that foreign keys work ...)
--
-- Revision 1.18  2006/06/15 21:04:18  ncq
-- - actually, only gm-dbo should be able to edit dem.staff
--
-- Revision 1.17  2006/05/15 14:47:27  ncq
-- - move inbox grants to inbox dynamic script
-- - include message pk into inbox view
--
-- Revision 1.16  2006/01/22 18:12:09  ncq
-- - grants for provider inbox view
--
-- Revision 1.15  2006/01/07 17:53:32  ncq
-- - proper grants for provider inbox
-- - dynamic staff re provider inbox added
--
-- Revision 1.14  2006/01/06 10:12:02  ncq
-- - add missing grants
-- - add_table_for_audit() now in "audit" schema
-- - demographics now in "dem" schema
-- - add view v_inds4vaccine
-- - move staff_role from clinical into demographics
-- - put add_coded_term() into "clin" schema
-- - put German things into "de_de" schema
--
-- Revision 1.13  2005/04/14 16:58:18  ncq
-- - gender_label grants
--
-- Revision 1.12  2005/04/12 16:23:23  ncq
-- - grant on name_gender_map
--
-- Revision 1.11  2005/03/31 17:47:52  ncq
-- - missing grant
--
-- Revision 1.10  2005/02/13 14:39:31  ncq
-- - do not grant DELETE on identity to gm-doctors
--
-- Revision 1.9  2005/02/12 13:49:14  ncq
-- - identity.id -> identity.pk
-- - allow NULL for identity.fk_marital_status
-- - subsequent schema changes
--
-- Revision 1.8  2005/01/24 17:57:43  ncq
-- - cleanup
-- - Ian's enhancements to address and forms tables
--
-- Revision 1.7  2004/12/21 09:59:40  ncq
-- - comm_channel -> comm else too long on server < 7.3
--
-- Revision 1.6  2004/12/20 19:04:37  ncq
-- - fixes by Ian while overhauling the demographics API
--
-- Revision 1.5  2004/07/20 07:12:16  ncq
-- - RW queries on state (and country) need rights on the primary key sequence, too
--
-- Revision 1.4  2004/07/20 00:02:54  ihaywood
-- grant the user access to the "state" table
--
-- Revision 1.3  2004/07/17 20:57:53  ncq
-- - don't use user/_user workaround anymore as we dropped supporting
--   it (but we did NOT drop supporting readonly connections on > 7.3)
--
-- Revision 1.2  2004/04/07 18:42:10  ncq
-- - *comm_channel -> *comm_chan
--
-- Revision 1.1  2004/04/07 18:29:28  ncq
-- - split out grants
--
