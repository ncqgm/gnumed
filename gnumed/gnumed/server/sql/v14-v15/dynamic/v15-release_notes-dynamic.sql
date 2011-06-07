-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

--set default_transaction_read_only to off;

-- --------------------------------------------------------------
INSERT INTO dem.message_inbox (
	fk_staff,
	fk_inbox_item_type,
	comment,
	data
) VALUES (
	(select pk from dem.staff where db_user = 'any-doc'),
	(select pk_type from dem.v_inbox_item_type where type = 'memo' and category = 'administrative'),
	'Release Notes for GNUmed 0.9.6 (database v15.6)',
	'GNUmed 0.9.6 Release Notes:

	Client 0.9.6

FIX: need to clear "Recent notes" sizer label between patients [thanks J.Busser]
FIX: exception on <DrugATC/> being returned from FreeDIAMS but empty [thanks ll]
FIX: exception (off-by-one) when splitting "incompletely" defined placeholders [thanks Marc]
FIX: exception when DOB=NULL when re-confirming old encounter [thanks J.Busser]

IMPROVED: enable detaching episodes from issues [thanks J.Busser]
');

-- --------------------------------------------------------------
