-- ==============================================================
-- GNUmed database schema change script
--
-- Source database version: v2
-- Target database version: v3
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
-- 
-- ==============================================================
-- $Id: dem-v_person_comms.sql,v 1.1 2006-11-20 15:53:41 ncq Exp $
-- $Revision: 1.1 $

-- --------------------------------------------------------------
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
drop view if exists dem.v_person_comms cascade;

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
