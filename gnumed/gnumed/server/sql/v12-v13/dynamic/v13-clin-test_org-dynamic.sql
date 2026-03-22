-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
-- $Id: v13-clin-test_org-dynamic.sql,v 1.1 2010-02-02 13:42:31 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
--set default_transaction_read_only to off;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- .contact
comment on column clin.test_org.contact is
	'free-text contact information for this lab';

alter table clin.test_org
	alter column contact
		set default null;

alter table clin.test_org drop constraint if exists sane_contact cascade;

alter table clin.test_org
	add constraint sane_contact
		check(gm.is_null_or_non_empty_string(contact) is True);


-- .internal_name
alter table clin.test_org
	alter column internal_name
		set not null;

alter table clin.test_org drop constraint if exists sane_internal_name cascade;

alter table clin.test_org
	add constraint sane_internal_name
		check(gm.is_null_or_blank_string(internal_name) is False);


-- .comment
alter table clin.test_org drop constraint if exists sane_comment cascade;

alter table clin.test_org
	add constraint sane_comment
		check(gm.is_null_or_non_empty_string(comment) is True);

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v13-clin-test_org-dynamic.sql,v $', '$Revision: 1.1 $');
