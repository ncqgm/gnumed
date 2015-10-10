-- project: GNUMed
-- database GIS - Canadian geographic information as per Jim Busser:
-- CA   CANADA
-- List source:   Canadian General Standards Board 
--                (CGSB), 1997-03-18; IGN 1989;
--                Canadian Postal Guide;
--                E-mail on Nunavut from Standards Council of Canada (SCC), 1999-09-02;
--                update 2001; update 2002
-- Code source:   Canadian Postal Guide
-- ===================================================================
-- author: Karsten Hilbert
-- license: GPL v2 or later

-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
insert into dem.state (code, country, name) values ('AB', 'CA', i18n.i18n('Alberta'));
insert into dem.state (code, country, name) values ('BC', 'CA', i18n.i18n('British Columbia'));
insert into dem.state (code, country, name) values ('MB', 'CA', i18n.i18n('Manitoba'));
insert into dem.state (code, country, name) values ('NB', 'CA', i18n.i18n('New Brunswick'));
insert into dem.state (code, country, name) values ('NL', 'CA', i18n.i18n('Newfoundland and Labrador'));
insert into dem.state (code, country, name) values ('NS', 'CA', i18n.i18n('Nova Scotia'));
insert into dem.state (code, country, name) values ('ON', 'CA', i18n.i18n('Ontario'));
insert into dem.state (code, country, name) values ('PE', 'CA', i18n.i18n('Prince Edward Island'));
insert into dem.state (code, country, name) values ('QC', 'CA', i18n.i18n('Quebec'));
insert into dem.state (code, country, name) values ('SK', 'CA', i18n.i18n('Saskatchewan'));
insert into dem.state (code, country, name) values ('NT', 'CA', i18n.i18n('Northwest Territories'));
insert into dem.state (code, country, name) values ('NU', 'CA', i18n.i18n('Nunavut'));
insert into dem.state (code, country, name) values ('YT', 'CA', i18n.i18n('Yukon Territory'));

select i18n.upd_tx('fr_CA', 'British Columbia', 'Colombie-Britannique');
select i18n.upd_tx('fr_CA', 'New Brunswick', 'Nouveau-Brunswick');
select i18n.upd_tx('fr_CA', 'Newfoundland and Labrador', 'Terre-Neuve-et-Labrador');
select i18n.upd_tx('fr_CA', 'Nova Scotia', 'Nouvelle-Écosse');
select i18n.upd_tx('fr_CA', 'Prince Edward Island', 'Île-du-Prince-Édouard');
select i18n.upd_tx('fr_CA', 'Quebec', 'Québec');
select i18n.upd_tx('fr_CA', 'Northwest Territories', 'Territoires du Nord-Ouest');
select i18n.upd_tx('fr_CA', 'Yukon Territory', 'Territoire du Yukon');

select dem.gm_upd_default_states();

-- ===================================================================
-- do simple revision tracking
delete from gm_schema_revision where filename = '$RCSfile: gmDemographics-Data.ca.sql,v $';
INSERT INTO gm_schema_revision (filename, version) VALUES('$RCSfile: gmDemographics-Data.ca.sql,v $', '$Revision: 1.5 $');
