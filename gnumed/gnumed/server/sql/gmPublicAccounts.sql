-- GNUmed PUBLIC database accounts

-- use for publicly accessible GNUmed databases

-- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
-- !! NEVER EVER use those accounts/passwords in a  !!
-- !! production database. As they are in CVS know- !!
-- !! ledge about them is PUBLIC and thus extremely !!
-- !! insecure. DO NOT USE FOR PRODUCTION.          !!
-- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
-- ===================================================================
-- Someone know a way of telling VALID UNTIL that the
-- value is CURRENT_DATE + interval '4 months' ?

-- ===================================================
select gm_create_user('any-doc', 'any-doc');

-- ===================================================
-- do simple schema revision tracking
-- not available just yet ...
--INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmPublicAccounts.sql,v $', '$Revision: 1.8 $') on conflict (filename, version) do nothing;
