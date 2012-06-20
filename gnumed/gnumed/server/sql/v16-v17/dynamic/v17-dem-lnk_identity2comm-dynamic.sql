-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
comment on column dem.lnk_identity2comm.comment is 'a comment on this communications channel';

\unset ON_ERROR_STOP
alter table dem.lnk_identity2comm drop constraint d_l_i2comm_sane_comment cascade;
\set ON_ERROR_STOP 1

alter table dem.lnk_identity2comm
	add constraint d_l_i2comm_sane_comment
		check (gm.is_null_or_non_empty_string(comment) is True);

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-dem-lnk_identity2comm-dynamic.sql', '17.0');
