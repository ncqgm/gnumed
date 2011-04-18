-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1
--set check_function_bodies to on;

-- --------------------------------------------------------------
GRANT "gm-public" TO "gm-staff";

-- --------------------------------------------------------------
-- FIXME: rework gm.create_user()
SELECT gm.create_user('any-staff', 'any-staff');

REVOKE "gm-doctors" from "any-staff";
GRANT "gm-staff" TO "any-staff";

-- --------------------------------------------------------------
select gm.log_script_insertion('v16-add_any-staff-dynamic.sql', 'Revision: 1');
