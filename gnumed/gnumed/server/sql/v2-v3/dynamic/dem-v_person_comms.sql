-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: dem-v_person_comms.sql,v 1.1 2006-11-20 15:53:41 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
\unset ON_ERROR_STOP
drop view dem.v_person_comms cascade;
\set ON_ERROR_STOP 1

create view dem.v_person_comms as

select
	li2c.id_identity as pk_identity,
	ect.description as comm_type,
	_(ect.description) as l10n_comm_type,
	li2c.url as url,
	li2c.is_confidential as is_confidential,
	li2c.id as pk_link_identity2comm,
	li2c.id_address as pk_address,
	li2c.id_type as pk_type
from
	dem.lnk_identity2comm li2c,
	dem.enum_comm_types ect
where
	li2c.id_type = ect.id
;


comment on view dem.v_person_comms is
	'denormalizes persons to communications channels';

-- --------------------------------------------------------------
grant select on dem.v_person_comms to group "gm-doctors";

-- --------------------------------------------------------------
select public.log_script_insertion('asdf$RCSfile: dem-v_person_comms.sql,v $', '$Revision: 1.1 $');

-- ==============================================================
-- $Log: dem-v_person_comms.sql,v $
-- Revision 1.1  2006-11-20 15:53:41  ncq
-- - needed by comms API
--
-- Revision 1.5  2006/10/24 13:09:45  ncq
-- - What it does duplicates the change log so axe it
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
