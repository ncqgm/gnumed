-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
-- $Id: v10-dem-v_provider_inbox.sql,v 1.2 2008-09-04 12:53:43 ncq Exp $
-- $Revision: 1.2 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view dem.v_provider_inbox cascade;
\set ON_ERROR_STOP 1


create view dem.v_provider_inbox as

select
	pi.modified_when as received_when,
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
	now() as received_when,
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

union

select
	now() as received_when,
	(select short_alias from dem.staff where dem.staff.pk = vtr.pk_intended_reviewer)
		as provider,
	0	as importance,
	'clinical'
		as category,
	_('clinical')
		as l10n_category,
	'review results'
		as type,
	_('review results')
		as l10n_type,
	(select _('unreviewed results for patient') || ' [' || vbp.lastnames || ', ' || vbp.firstnames || ']'
	 from dem.v_basic_person vbp
	 where vbp.pk_identity = vtr.pk_patient
	)	as comment,
	vtr.pk_patient
		as pk_context,
	NULL
		as data,
	NULL
		as pk_provider_inbox,
	vtr.pk_intended_reviewer
		as pk_staff,
	(select pk_category from dem.v_inbox_item_type where type='review results')
		as pk_category,
	(select pk_type from dem.v_inbox_item_type where type='review results')
		as pk_type
from
	clin.v_test_results vtr
where
	reviewed is False

;


comment on view dem.v_provider_inbox is
'Denormalized messages for the providers.
Using UNION makes sure we get the right level of uniqueness.';


grant select on dem.v_provider_inbox to group "gm-doctors";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v10-dem-v_provider_inbox.sql,v $', '$Revision: 1.2 $');

-- ==============================================================
-- $Log: v10-dem-v_provider_inbox.sql,v $
-- Revision 1.2  2008-09-04 12:53:43  ncq
-- - include received_when column
--
-- Revision 1.1  2008/09/02 18:56:39  ncq
-- - new
--
--