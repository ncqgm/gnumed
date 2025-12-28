-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

set check_function_bodies to on;

-- --------------------------------------------------------------
drop function if exists gm.user_needs_md5_2_scramsha256_pwd_switch(IN _user TEXT) cascade;

create or replace function gm.user_needs_md5_2_scramsha256_pwd_switch(IN _user TEXT)
	returns boolean
	language 'plpgsql'
	security definer
	as '
BEGIN
	PERFORM 1 FROM pg_authid WHERE
		rolname = _user
			AND
		rolpassword LIKE ''md5%'';
	IF NOT FOUND THEN
		RETURN FALSE;
	END IF;
	RAISE NOTICE ''gm.user_needs_md5_2_scramsha256_pwd_switch: account [%] needs to re-set password for encryption method switch'', _user;
	RETURN TRUE;
END;';

COMMENT ON FUNCTION gm.user_needs_md5_2_scramsha256_pwd_switch(IN _user TEXT) IS
'Check if a given user needs to renew the password for making the encryption method switch.';

-- --------------------------------------------------------------
select gm.log_script_insertion('v22-gm-user_needs_md5_2_scramsha256_pwd_switch.sql', '22.33');
