-- Project: GnuMed
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmDemographics-Grants.sql,v $
-- $Revision: 1.3 $
-- license: GPL
-- authors: Ian Haywood, Horst Herb, Karsten Hilbert, Richard Terry

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

GRANT SELECT, INSERT, UPDATE, DELETE ON
	names,
	names_id_seq,
	identity,
	identity_id_seq,
	urb,
	urb_id_seq,
	country,
	street,
	street_id_seq,
	address,
	address_id_seq,
	address_type,
	address_type_id_seq,
	enum_comm_types,
	comm_channel,
	comm_channel_id_seq,
	enum_ext_id_types,
	lnk_identity2ext_id,
	lnk_identity2ext_id_id_seq,
	mapbook,
	coordinate,
	coordinate_id_seq,
	address_info,
	address_info_id_seq,
	lnk_person_org_address,
	lnk_person_org_address_id_seq,
	lnk_identity2comm_chan,
	lnk_identity2comm_chan_id_seq,
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
	lnk_org2comm_channel,
	lnk_org2comm_channel_id_seq,
	staff_role,
	staff,
	marital_status
TO GROUP "gm-doctors";

-- ===================================================================
-- $Log: gmDemographics-Grants.sql,v $
-- Revision 1.3  2004-07-17 20:57:53  ncq
-- - don't use user/_user workaround anymore as we dropped supporting
--   it (but we did NOT drop supporting readonly connections on > 7.3)
--
-- Revision 1.2  2004/04/07 18:42:10  ncq
-- - *comm_channel -> *comm_chan
--
-- Revision 1.1  2004/04/07 18:29:28  ncq
-- - split out grants
--
