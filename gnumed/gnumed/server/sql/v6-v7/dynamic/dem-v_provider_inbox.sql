-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v6
-- Target database version: v7
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: dem-v_provider_inbox.sql,v 1.1 2007-06-11 19:46:11 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view dem.v_provider_inbox cascade;
\set ON_ERROR_STOP 1

-- ---------------------------------------------
create view dem.v_provider_inbox as
select
	(select short_alias from dem.staff where dem.staff.pk = pi.fk_staff) as provider,
	pi.importance,
	vit.category,
	vit.l10n_category,
	vit.type,
	vit.l10n_type,
	pi.comment,
	pi.ufk_context as pk_context,
	pi.data as data,
	pi.pk as pk_provider_inbox,
	pi.fk_staff as pk_staff,
	vit.pk_category,
	pi.fk_inbox_item_type as pk_type
from
	dem.provider_inbox pi,
	dem.v_inbox_item_type vit
where
	pi.fk_inbox_item_type = vit.pk_type

union

select
	(select short_alias from dem.staff where dem.staff.pk = vo4dnd.pk_intended_reviewer)
		as provider,
	0	as importance,
	'clinical'
		as category,
	_('clinical')
		as l10n_category,
	'review docs'
		as type,
	_('review docs')
		as l10n_type,
	(select _('unreviewed documents for patient') || ' [' || vbp.lastnames || ', ' || vbp.firstnames || ']'
	 from dem.v_basic_person vbp
	 where vbp.pk_identity=vo4dnd.pk_patient)
	 	as comment,
	vo4dnd.pk_patient
		as pk_context,
	NULL
		as data,
	NULL
		as pk_provider_inbox,
	vo4dnd.pk_intended_reviewer
		as pk_staff,
	(select pk_category from dem.v_inbox_item_type where type='review docs')
		as pk_category,
	(select pk_type from dem.v_inbox_item_type where type='review docs')
		as pk_type
from
	blobs.v_obj4doc_no_data vo4dnd
where
	reviewed is False
;

comment on view dem.v_provider_inbox is
	'Denormalized messages for the providers.';

-- --------------------------------------------------------------
grant select on dem.v_provider_inbox to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: dem-v_provider_inbox.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: dem-v_provider_inbox.sql,v $
-- Revision 1.1  2007-06-11 19:46:11  ncq
-- - new
--
-- Revision 1.1  2007/03/08 15:10:52  ncq
-- - add filename to blobs object view
--
-- Revision 1.1  2006/10/08 08:53:24  ncq
-- - got dropped by other changes
--
-- Revision 1.4  2006/09/28 14:39:51  ncq
-- - add comment template
--
-- Revision 1.3  2006/09/18 17:32:53  ncq
-- - make more fool-proof
--
-- Revision 1.2  2006/09/16 21:47:37  ncq
-- - improvements
--
-- Revision 1.1  2006/09/16 14:02:36  ncq
-- - use this as a template for change scripts
--
--
