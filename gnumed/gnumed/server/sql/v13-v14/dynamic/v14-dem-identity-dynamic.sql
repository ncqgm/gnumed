-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
-- 
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
-- .emergency_contact
comment on column dem.identity.emergency_contact is
	'Free text emergency contact information.';


\unset ON_ERROR_STOP
alter table dem.identity drop constraint sane_emergency_contact cascade;
\set ON_ERROR_STOP 1


alter table dem.identity
	add constraint sane_emergency_contact
		check (gm.is_null_or_non_empty_string(emergency_contact) is True);



-- .fk_emergency_contact
comment on column dem.identity.fk_emergency_contact is
	'Link to another dem.identity to be used as emergency contact.';


alter table dem.identity
	add foreign key (fk_emergency_contact) references dem.identity(pk)
		on update cascade
		on delete restrict;



-- .comment
comment on column dem.identity.comment is
	'A free-text comment on this identity.';


\unset ON_ERROR_STOP
alter table dem.identity drop constraint sane_comment cascade;
\set ON_ERROR_STOP 1


alter table dem.identity
	add constraint sane_comment
		check (gm.is_null_or_non_empty_string(comment) is True);

-- --------------------------------------------------------------
select gm.log_script_insertion('v14-dem-identity-dynamic.sql', 'Revision: 1.1');
