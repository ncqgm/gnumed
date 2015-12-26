-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

-- --------------------------------------------------------------
drop view if exists dem.v_basic_person cascade;

create or replace view dem.v_basic_person as
select d_vp.*
from dem.v_persons d_vp
where
	d_vp.is_deleted is false
;


comment on view dem.v_basic_person is
	'This view denormalizes non-deleted persons with their active name.';


revoke all on dem.v_basic_person from public;
grant select on dem.v_basic_person to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('v21-dem-v_basic_person.sql', '21.0');
