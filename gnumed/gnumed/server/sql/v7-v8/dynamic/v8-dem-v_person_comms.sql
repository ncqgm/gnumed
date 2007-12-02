-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: v8-dem-v_person_comms.sql,v 1.1 2007-12-02 13:44:53 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop function dem.link_person_comm(integer, text, text, bool) cascade;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view dem.v_person_comms_flat cascade;
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view dem.v_person_comms cascade;
\set ON_ERROR_STOP 1

create view dem.v_person_comms as
select
	li2c.fk_identity as pk_identity,
	ect.description as comm_type,
	_(ect.description) as l10n_comm_type,
	li2c.url as url,
	li2c.is_confidential as is_confidential,
	li2c.pk as pk_link_identity2comm,
	li2c.fk_address as pk_address,
	li2c.fk_type as pk_type
from
	dem.lnk_identity2comm li2c,
	dem.enum_comm_types ect
where
	li2c.fk_type = ect.pk
;


comment on view dem.v_person_comms is
	'denormalizes persons to communications channels';


grant select on dem.v_person_comms to group "gm-public";

-- --------------------------------------------------------------
select gm.log_script_insertion('$RCSfile: v8-dem-v_person_comms.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: v8-dem-v_person_comms.sql,v $
-- Revision 1.1  2007-12-02 13:44:53  ncq
-- - cleanup
--
--