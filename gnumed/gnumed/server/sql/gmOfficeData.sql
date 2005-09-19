-- GnuMed office related/administrative data

-- This is free software in the sense of the General Public License (GPL)
-- For details regarding GPL licensing see http://gnu.org

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmOfficeData.sql,v $
-- $Revision: 1.5 $ $Date: 2005-09-19 16:38:51 $ $Author: ncq $
-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
-- forms handling
-- ===================================================================
-- form job targets
insert into form_job_targets (target) values (_('printer'));
insert into form_job_targets (target) values (_('fax'));
insert into form_job_targets (target) values (_('email'));

-- ===================================================================
-- billing schemes
--insert into billing_scheme (name, iso_countrycode) values ('Bulk-billed Medicare', 'au');
--insert into billing_scheme (name, iso_countrycode) values ('Private Billing', 'au');
--insert into billing_scheme (name, iso_countrycode) values ('Veteran''s Affairs', 'au');
--insert into billing_scheme (name, iso_countrycode) values ('WorkCover', 'au');

-- ===================================================================
-- Warning: translate, but DON'T alter the order!!!
--insert into accounts (name) values ('Assets');
--insert into accounts (name) values ('Liabilities');
--insert into accounts (parent, name) values (1, 'Accounts Recievable');
--insert into accounts (parent, name) values (2, 'Accounts Payable');
--insert into accounts (parent, name) values (2, 'Capital'); 
--insert into accounts (parent, name) values (3, 'Patients');
--insert into accounts (parent, name) values (4, 'Tax');
--insert into accounts (parent, name) values (4, 'Wages'); 
--insert into accounts (parent, name) values (1, 'Cash');
--insert into accounts (parent, name) values (1, 'Inventory');

-- ===================================================================
-- do simple schema revision tracking
delete from gm_schema_revision where filename='$RCSfile: gmOfficeData.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmOfficeData.sql,v $', '$Revision: 1.5 $');

-- ===================================================================
-- $Log: gmOfficeData.sql,v $
-- Revision 1.5  2005-09-19 16:38:51  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.4  2005/07/14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.3  2005/01/29 18:34:14  ncq
-- - form_queue_types renamed to the more appropriate form_job_targets
--
-- Revision 1.2  2005/01/12 12:29:29  ncq
-- - comment out some unused tables
--
-- Revision 1.1  2004/03/09 23:58:56  ncq
-- - first version
--
