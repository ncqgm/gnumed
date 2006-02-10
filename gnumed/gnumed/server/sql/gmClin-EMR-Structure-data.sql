-- Project: GNUmed - EMR structure related tables:
--		- health issues
--		- encounters
--		- episodes
-- ===================================================================
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmClin-EMR-Structure-data.sql,v $
-- $Revision: 1.1 $
-- license: GPL
-- author: Ian Haywood, Karsten Hilbert

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
--		self.__consultation_types = [
--			_('in surgery'),
--			_('home visit'),
--			_('by phone'),
--			_('at specialist'),
--			_('patient absent'),
--			_('by email'),
--			_('other consultation')
--		]
INSERT INTO clin.encounter_type (description) values (i18n.i18n('in surgery'));
INSERT INTO clin.encounter_type (description) values (i18n.i18n('phone consultation'));
INSERT INTO clin.encounter_type (description) values (i18n.i18n('fax consultation'));
INSERT INTO clin.encounter_type (description) values (i18n.i18n('home visit'));
INSERT INTO clin.encounter_type (description) values (i18n.i18n('nursing home visit'));
INSERT INTO clin.encounter_type (description) values (i18n.i18n('repeat script'));
INSERT INTO clin.encounter_type (description) values (i18n.i18n('hospital visit'));
INSERT INTO clin.encounter_type (description) values (i18n.i18n('video conference'));
INSERT INTO clin.encounter_type (description) values (i18n.i18n('proxy encounter'));
INSERT INTO clin.encounter_type (description) values (i18n.i18n('emergency encounter'));
INSERT INTO clin.encounter_type (description) values (i18n.i18n('chart review'));
INSERT INTO clin.encounter_type (description) values (i18n.i18n('other encounter'));



-- ===================================================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmClin-EMR-Structure-data.sql,v $', '$Revision: 1.1 $');

-- ===================================================================
-- $Log: gmClin-EMR-Structure-data.sql,v $
-- Revision 1.1  2006-02-10 14:08:58  ncq
-- - factor out EMR structure clinical schema into its own set of files
--
--
