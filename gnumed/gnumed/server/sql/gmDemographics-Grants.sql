-- Project: GnuMed
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmDemographics-Grants.sql,v $
-- $Revision: 1.12 $
-- license: GPL
-- authors: Ian Haywood, Horst Herb, Karsten Hilbert, Richard Terry

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

grant select on
	name_gender_map
to group "gm-public";

-- do not allow anyone other the gm-dbo to DELETE on identity ...
grant select, insert, update on
	identity,
	identity_pk_seq
to group "gm-doctors";

GRANT SELECT, INSERT, UPDATE, DELETE ON
	names,
	names_id_seq,
	urb,
	urb_id_seq,
	country,
	country_id_seq,
	state,
	state_id_seq,
	street,
	street_id_seq,
	address,
	address_id_seq,
	address_type,
	address_type_id_seq,
	enum_comm_types,
	enum_ext_id_types,
	enum_ext_id_types_pk_seq,
	lnk_identity2ext_id,
	lnk_identity2ext_id_id_seq,
	lnk_person_org_address,
	lnk_person_org_address_id_seq,
	lnk_identity2comm,
	lnk_identity2comm_id_seq,
	relation_types,
	lnk_person2relative,
	lnk_person2relative_id_seq,
	occupation,
	occupation_id_seq,	
	lnk_job2person,
	lnk_job2person_id_seq,
	org_category,
	org,
	org_id_seq,
	lnk_org2comm,
	lnk_org2comm_id_seq,
	staff_role,
	staff,
	marital_status
TO GROUP "gm-doctors";

-- ===================================================================
-- $Log: gmDemographics-Grants.sql,v $
-- Revision 1.12  2005-04-12 16:23:23  ncq
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
