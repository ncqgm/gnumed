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
delete from ref.keyword_expansion where keyword = 'autograph-LMcC';

insert into ref.keyword_expansion (
	fk_staff,
	keyword,
	textual_data
) values (
	null,
	'autograph-LMcC',
	'Leonard McCoy autograph'
);

-- --------------------------------------------------------------
select gm.log_script_insertion('v18-LMcC_autograph.sql', '18.0');
