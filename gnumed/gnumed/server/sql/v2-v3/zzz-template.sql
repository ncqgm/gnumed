-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: 
--
-- ==============================================================
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- remember to handle dependant objects possibly dropped by CASCADE
\unset ON_ERROR_STOP
drop forgot_to_edit_drops cascade;
\set ON_ERROR_STOP 1


comment on column/table .forgot_to_edit_comment. is
	'';

-- --------------------------------------------------------------
-- don't forget appropriate grants
grant select, insert, update, delete on
	.forgot_to_edit_grants
to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('filename.sql', 'xx.y');
