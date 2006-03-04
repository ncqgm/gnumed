-- Project: GNUmed - vaccination related data
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmClin-Vaccination-data.sql,v $
-- $Revision: 1.3 $
-- license: GPL
-- author: Ian Haywood, Karsten Hilbert, Richard Terry

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
-- vaccination routes
delete from clin.vacc_route;

insert into clin.vacc_route
	(abbreviation, description)
values
	('i.m.', i18n.i18n('intramuscular'));

insert into clin.vacc_route
	(abbreviation, description)
values
	('s.c.', i18n.i18n('subcutaneous'));

insert into clin.vacc_route 
	( abbreviation, description) 
values 
	( 'o', i18n.i18n('orally'));

-- ===================================================================
-- vaccination indications
delete from clin.vacc_indication;

insert into clin.vacc_indication (description) values (i18n.i18n('cholera'));
insert into clin.vacc_indication (description) values (i18n.i18n('Coxiella burnetii'));
insert into clin.vacc_indication (description) values (i18n.i18n('diphtheria'));
insert into clin.vacc_indication (description) values (i18n.i18n('haemophilus influenzae b'));
insert into clin.vacc_indication (description) values (i18n.i18n('hepatitis A'));
insert into clin.vacc_indication (description) values (i18n.i18n('hepatitis B'));
insert into clin.vacc_indication (description) values (i18n.i18n('influenza'));
insert into clin.vacc_indication (description) values (i18n.i18n('japanese B encephalitis'));
insert into clin.vacc_indication (description) values (i18n.i18n('measles'));
insert into clin.vacc_indication (description) values (i18n.i18n('meningococcus A'));
insert into clin.vacc_indication (description) values (i18n.i18n('meningococcus C'));
insert into clin.vacc_indication (description) values (i18n.i18n('meningococcus W'));
insert into clin.vacc_indication (description) values (i18n.i18n('meningococcus Y'));
insert into clin.vacc_indication (description) values (i18n.i18n('mumps'));
insert into clin.vacc_indication (description) values (i18n.i18n('pertussis'));
insert into clin.vacc_indication (description) values (i18n.i18n('pneumococcus'));
insert into clin.vacc_indication (description) values (i18n.i18n('poliomyelitis'));
insert into clin.vacc_indication (description) values (i18n.i18n('rabies'));
insert into clin.vacc_indication (description) values (i18n.i18n('rubella'));
insert into clin.vacc_indication (description) values (i18n.i18n('tetanus'));
insert into clin.vacc_indication (description) values (i18n.i18n('tick-borne meningoencephalitis'));
insert into clin.vacc_indication (description) values (i18n.i18n('salmonella typhi'));
insert into clin.vacc_indication (description) values (i18n.i18n('varicella'));
insert into clin.vacc_indication (description) values (i18n.i18n('yellow fever'));
insert into clin.vacc_indication (description) values (i18n.i18n('yersinia pestis'));

insert into clin.vaccination_course_constraint (description) values (i18n.i18n('female only'));
insert into clin.vaccination_course_constraint (description) values (i18n.i18n('aboriginal/tsi only'));
insert into clin.vaccination_course_constraint (description) values (i18n.i18n('seasonal'));
--insert into clin.vaccination_course_constraint (description) values (i18n.i18n(''));
--insert into clin.vaccination_course_constraint (description) values (i18n.i18n(''));

-- ===================================================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmClin-Vaccination-data.sql,v $', '$Revision: 1.3 $');

-- ===================================================================
-- $Log: gmClin-Vaccination-data.sql,v $
-- Revision 1.3  2006-03-04 16:16:27  ncq
-- - adjust to regime -> course name change
-- - enhanced comments
-- - audit more tables
-- - add v_vaccination_courses_in_schedule
-- - adjust grants
--
-- Revision 1.2  2006/02/19 13:45:05  ncq
-- - move the rest of the dynamic vacc stuff from gmClinicalViews.sql
--   into gmClin-Vaccination-dynamic.sql
-- - add vaccination schedule constraint enumeration data
-- - add is_active to clin.vaccination_course
-- - add clin.vacc_regime_constraint
-- - add clin.lnk_constraint2vacc_reg
-- - proper grants
--
-- Revision 1.1  2006/02/08 15:15:39  ncq
-- - factor our vaccination stuff into its own set of files
-- - remove clin.lnk_vacc_ind2code in favour of clin.coded_term usage
-- - improve comments as discussed on the list
--
--
