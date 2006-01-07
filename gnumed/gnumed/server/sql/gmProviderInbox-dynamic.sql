-- =============================================
-- GNUmed - dynamic tables for the provider inbox
-- =============================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmProviderInbox-dynamic.sql,v $
-- $Id: gmProviderInbox-dynamic.sql,v 1.2 2006-01-07 17:53:32 ncq Exp $
-- license: GPL
-- author: Karsten.Hilbert@gmx.net

-- =============================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ---------------------------------------------
comment on table dem.inbox_item_type is
	'Holds the various types of messages that can show up in the provider inbox.';

-- ---------------------------------------------
comment on table dem.provider_inbox is
	'Holds per-provider messages.';
comment on column dem.provider_inbox.fk_staff is
	'the member of staff this message is addressed to';
comment on column dem.provider_inbox.fk_inbox_item_type is
	'the item (message) type';
comment on column dem.provider_inbox.comment is
	'a free-text comment, may be NULL';
comment on column dem.provider_inbox.ufk_context is
	'an optional, *u*nchecked *f*oreign *k*ey, it is up to
	 the application to know what to do with this, it will
	 have to make sense within the context of the combination
	 of staff ID, item type, and comment';
comment on column dem.provider_inbox.importance is
	'the relative importance of this message:\n
	 -1: lower than most things already in the inbox ("low")\n
	  0: same as most things ("standard")\n
	  1: higher than most things already there ("high")';

-- ---------------------------------------------
\unset ON_ERROR_STOP
drop view dem.v_provider_inbox cascade;
\set ON_ERROR_STOP 1

create view dem.v_provider_inbox as
select
	(select sign from dem.staff where dem.staff.pk = pi.fk_staff)
		as provider,
	(select description from dem.inbox_item_type where dem.inbox_item_type=pi.fk_inbox_item_type)
		as type,
	(select _(description) from dem.inbox_item_type where dem.inbox_item_type=pi.fk_inbox_item_type)
		as l10n_type,
	pi.comment,
	pi.ufk_context as pk_context,
	pi.importance,
	pi.fk_staff as pk_staff,
	pi.fk_inbox_item_type as pk_inbox_item_type,
	pi.pk as pk_provider_inbox
from
	dem.provider_inbox pi
where
;

-- =============================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmProviderInbox-dynamic.sql,v $2', '$Revision: 1.2 $');

-- =============================================
-- $Log: gmProviderInbox-dynamic.sql,v $
-- Revision 1.2  2006-01-07 17:53:32  ncq
-- - proper grants for provider inbox
-- - dynamic staff re provider inbox added
--
-- Revision 1.1  2006/01/07 15:22:23  ncq
-- - initial attempt at provider inbox tables
--
