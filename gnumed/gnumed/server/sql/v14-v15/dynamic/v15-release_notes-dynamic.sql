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
	'Release Notes for GNUmed 0.9.9 (database v15.9)',
	'GNUmed 0.9.9 Release Notes:

	0.9.9

FIX: be ever more careful on list ctrl item tooltip generation [thanks Marc]

	0.9.8

FIX: exception on trying to create Gelbe Liste/MMI version file [thanks ALI from Lebanon]
FIX: exceptions on various TWAIN error states [thanks ALI from Lebanon]
FIX: failure to save leftmost notelet editor on [Save all] button [thanks J.Busser]
FIX: exception on not selecting an encounter for [Save under] action [thanks J.Busser]
FIX: improper scaling of "width < height" images (visual progress notes)
FIX: exception on wx.TreeCtrl.GetPyItemData() w/o *explicit* wx.TR_SINGLE style
FIX: improper sizing of SOAP expandos on Windows (#646240) [thanks S.Hilbert]
FIX: exception on getting list item tooltip if no data available [thanks J.Busser]
FIX: exception on selecting bytea columns in report generator [thanks J.Busser]

IMPROVED: also try %d/%m/%Y when parsing dates [thanks J.Busser]
');

-- --------------------------------------------------------------
