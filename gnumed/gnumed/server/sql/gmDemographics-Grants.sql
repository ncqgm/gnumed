-- Project: GnuMed
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmDemographics-Grants.sql,v $
-- $Revision: 1.1 $
-- license: GPL
-- authors: Ian Haywood, Horst Herb, Karsten Hilbert, Richard Terry

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

GRANT SELECT ON
	names,
	identity,
	identity_id_seq,
	urb,
	country,
	street,
	address,
	address_type,
	state,
	enum_comm_types,
	enum_ext_id_types,
	comm_channel,
	lnk_identity2ext_id,
	mapbook,
	coordinate,
	address_info,
	lnk_person_org_address,
	lnk_identity2comm_channel,
	relation_types,
	lnk_person2relative,
	occupation,
	lnk_job2person,
	org_category,
	org,
	lnk_org2comm_channel,
	staff_role,
	staff,
	marital_status
TO GROUP "gm-doctors";

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
	comm_channel,
	comm_channel_id_seq,
	lnk_identity2ext_id,
	lnk_identity2ext_id_id_seq,
	coordinate,
	coordinate_id_seq,
	address_info,
	address_info_id_seq,
	lnk_person_org_address,
	lnk_person_org_address_id_seq,
	lnk_identity2comm_channel,
	lnk_identity2comm_channe_id_seq,
	lnk_person2relative,
	lnk_person2relative_id_seq,
	occupation,
	occupation_id_seq,	
	lnk_job2person,
	lnk_job2person_id_seq,
	org,
	org_id_seq,
	lnk_org2comm_channel,
	lnk_org2comm_channel_id_seq
TO GROUP "_gm-doctors";

-- ===================================================================
-- $Log: gmDemographics-Grants.sql,v $
-- Revision 1.1  2004-04-07 18:29:28  ncq
-- - split out grants
--
