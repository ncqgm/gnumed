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
	'Release Notes for GNUmed 0.9.3 (database v15.3)',
	'GNUmed 0.9.3 Release Notes:

	0.9.3

FIX: wxPython-MacOSX needs yet another way to detach sizer items [thanks J.Busser]

IMPROVED: naming of formatted item view in tree (Details -> Synopsis) [thanks J.Busser]
IMRPOVED: synopsis formatting of episodes in EMR tree [thanks J.Busser]
IMPROVED: wording of problem list headers in SOAP plugin [thanks S.Leibner]
IMRPOVED: synopsis formatting of health issues in EMR tree [thanks J.Busser]
IMPROVED: problem list formatting in SOAP plugin [thanks J.Busser]
');

-- --------------------------------------------------------------
