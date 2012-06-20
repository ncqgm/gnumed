-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1
set check_function_bodies to on;

--set default_transaction_read_only to off;

-- --------------------------------------------------------------
-- REVOKEs
revoke SELECT on
	blobs.v_doc_type
	, blobs.doc_type

	, dem.address
	, dem.address_id_seq
	, dem.address_type
	, dem.address_type_id_seq
	, dem.street
	, dem.street_id_seq
	, dem.urb
	, dem.urb_id_seq
	, dem.state
	, dem.state_id_seq
	, dem.country
	, dem.country_id_seq
	, dem.lnk_person_org_address_id_seq
	, dem.v_address
from group "gm-doctors";

revoke UPDATE on
	dem.address_type_id_seq
	, dem.address_id_seq
	, dem.street_id_seq
	, dem.urb_id_seq
	, dem.state_id_seq
	, dem.country_id_seq
	, dem.lnk_person_org_address_id_seq
from group "gm-doctors";

-- --------------------------------------------------------------
-- "gm-public"
-- --------------------------------------------------------------
-- SELECT
grant SELECT on
	ref.v_tag_images_no_data

	, dem.lnk_identity2comm
	, dem.enum_comm_types
	, dem.address
	, dem.address_type
	, dem.street
	, dem.urb
	, dem.state
	, dem.country
	, dem.v_zip2data
	, dem.v_address

	, blobs.v_doc_type
	, blobs.doc_type
to group "gm-public";

-- sequence USAGE
grant USAGE on
	dem.lnk_identity2comm_id_seq
	, dem.lnk_identity2ext_id_id_seq
	, dem.address_id_seq
	, dem.address_type_id_seq
	, dem.street_id_seq
	, dem.urb_id_seq
	, dem.state_id_seq
	, dem.country_id_seq

	, clin.allergy_state_id_seq
	, clin.waiting_list_pk_seq
to group "gm-public";

-- --------------------------------------------------------------
-- "gm-doctors"
-- --------------------------------------------------------------
grant USAGE on
	dem.lnk_person_org_address_id_seq
to group "gm-doctors";

-- --------------------------------------------------------------
-- "gm-staff"
-- --------------------------------------------------------------
-- SELECT
grant SELECT on
	dem.v_message_inbox
	, dem.staff
	, dem.v_person_comms
	, dem.lnk_identity2ext_id
	, dem.lnk_person_org_address

	, clin.waiting_list

	, blobs.doc_med
to group "gm-staff";

-- --------------------------------------------------------------
-- USAGE
grant USAGE on
	dem.lnk_person_org_address_id_seq
to group "gm-staff";

-- --------------------------------------------------------------
-- INSERT/UPDATE/DELETE
grant INSERT, UPDATE, DELETE on
	dem.lnk_identity2comm
	, dem.enum_comm_types
	, dem.lnk_identity2ext_id
	, dem.address
	, dem.address_type
	, dem.street
	, dem.urb
	, dem.state
	, dem.country
	, dem.lnk_person_org_address

	, clin.waiting_list

	, blobs.doc_type
	, blobs.doc_med
to group "gm-staff";

-- --------------------------------------------------------------
create or replace function clin.get_hints_for_patient(integer)
	returns setof ref.auto_hint
	language 'plpgsql'
	as '
DECLARE
	_pk_identity ALIAS FOR $1;
	_r ref.auto_hint%rowtype;
	_query text;
	_applies boolean;
BEGIN
	FOR _r IN SELECT * FROM ref.auto_hint WHERE is_active LOOP
		_query := replace(_r.query, ''ID_ACTIVE_PATIENT'', _pk_identity::text);
		--RAISE NOTICE ''%'', _query;
		BEGIN
			EXECUTE _query INTO STRICT _applies;
			--RAISE NOTICE ''Applies: %'', _applies;
			IF _applies THEN
				RETURN NEXT _r;
			END IF;
		EXCEPTION
			WHEN insufficient_privilege THEN RAISE NOTICE ''auto hint query failed: %'', _query;
				-- should bring this to the attention of the user somehow
		END;
	END LOOP;
	RETURN;
END;';

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-role-gm_staff-permissions.sql', '18.0');
