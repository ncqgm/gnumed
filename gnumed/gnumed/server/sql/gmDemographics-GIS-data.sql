-- project: GNUMed
-- database: GIS
-- purpose:  geographic information (mostly of type 'address')

-- license: GPL (details at http://gnu.org)
-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/server/sql/gmDemographics-GIS-data.sql,v $
-- $Id $
-- ===================================================================
-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- ===================================================================
--insert:
--v_enum_comm_types:
--	Home_Phone text,
--	Work_Phone text,
--	Fax text,
--	email text,
--	internet text,
--	mobile text,

-- ===================================================================
-- do NOT alter the id of home or work !
INSERT INTO address_type(id, name) values(1, i18n('home'));
INSERT INTO address_type(id, name) values(2, i18n('work'));
INSERT INTO address_type(id, name) values(3, i18n('parents'));
INSERT INTO address_type(id, name) values(4, i18n('holidays'));
INSERT INTO address_type(id, name) values(5, i18n('temporary'));

-- comms types. Don't change ID numbers

insert into enum_comm_types (id, description) values (1, i18n('email'));
insert into enum_comm_types (id, description) values (2, i18n('fax'));
insert into enum_comm_types (id, description) values (3, i18n('homephone'));
insert into enum_comm_types (id, description) values (4, i18n('workphone'));
insert into enum_comm_types (id, description) values (5, i18n('mobile'));
insert into enum_comm_types (id, description) values (6, i18n('web'));
insert into enum_comm_types (id, description) values (7, i18n('jabber'));


-- ===================================================================
-- here come the ISO country codes ...

insert into country(code, name) values('AF', i18n('Afghanistan'));
insert into country(code, name) values('AL', i18n('Albania'));
insert into country(code, name) values('DZ', i18n('Algeria'));
insert into country(code, name) values('AS', i18n('American Samoa'));
insert into country(code, name) values('AD', i18n('Andorra'));
insert into country(code, name) values('AO', i18n('Angola'));
insert into country(code, name) values('AI', i18n('Anguilla'));
insert into country(code, name) values('AQ', i18n('Antarctica'));
insert into country(code, name) values('AG', i18n('Antigua and Barbuda'));
insert into country(code, name) values('AR', i18n('Argentina'));
insert into country(code, name) values('AM', i18n('Armenia'));
insert into country(code, name) values('AW', i18n('Aruba'));
insert into country(code, name) values('AU', i18n('Australia'));
insert into country(code, name) values('AT', i18n('Austria'));
insert into country(code, name) values('AZ', i18n('Azerbaijan'));
insert into country(code, name) values('BS', i18n('Bahamas'));
insert into country(code, name) values('BH', i18n('Bahrain'));
insert into country(code, name) values('BD', i18n('Bangladesh'));
insert into country(code, name) values('BB', i18n('Barbados'));
insert into country(code, name) values('BY', i18n('Belarus'));
insert into country(code, name) values('BE', i18n('Belgium'));
insert into country(code, name) values('BZ', i18n('Belize'));
insert into country(code, name) values('BJ', i18n('Benin'));
insert into country(code, name) values('BM', i18n('Bermuda'));
insert into country(code, name) values('BT', i18n('Bhutan'));
insert into country(code, name) values('BO', i18n('Bolivia'));
insert into country(code, name) values('BA', i18n('Bosnia and Herzegovina'));
insert into country(code, name) values('BW', i18n('Botswana'));
insert into country(code, name) values('BV', i18n('Bouvet Island'));
insert into country(code, name) values('BR', i18n('Brazil'));
insert into country(code, name) values('IO', i18n('British Indian Ocean Territory'));
insert into country(code, name) values('BN', i18n('Brunei Darussalam'));
insert into country(code, name) values('BG', i18n('Bulgaria'));
insert into country(code, name) values('BF', i18n('Burkina Faso'));
insert into country(code, name) values('BI', i18n('Burundi'));
insert into country(code, name) values('KH', i18n('Cambodia'));
insert into country(code, name) values('CM', i18n('Cameroon'));
insert into country(code, name) values('CA', i18n('Canada'));
insert into country(code, name) values('CV', i18n('Cape Verde'));
insert into country(code, name) values('KY', i18n('Cayman Islands'));
insert into country(code, name) values('CF', i18n('Central African Republic'));
insert into country(code, name) values('TD', i18n('Chad'));
insert into country(code, name) values('CL', i18n('Chile'));
insert into country(code, name) values('CN', i18n('China'));
insert into country(code, name) values('CX', i18n('Christmas Island'));
insert into country(code, name) values('CC', i18n('Cocos (Keeling) Islands'));
insert into country(code, name) values('CO', i18n('Colombia'));
insert into country(code, name) values('KM', i18n('Comoros'));
insert into country(code, name) values('CG', i18n('Congo'));
insert into country(code, name) values('CD', i18n('Congo, The Democratic Republic'));
insert into country(code, name) values('CK', i18n('Cook Islands'));
insert into country(code, name) values('CR', i18n('Costa Rica'));
insert into country(code, name) values('CI', i18n('Cote D''Ivoire'));
insert into country(code, name) values('HR', i18n('Croatia'));
insert into country(code, name) values('CU', i18n('Cuba'));
insert into country(code, name) values('CY', i18n('Cyprus'));
insert into country(code, name) values('CZ', i18n('Czech Republic'));
insert into country(code, name) values('DK', i18n('Denmark'));
insert into country(code, name) values('DJ', i18n('Djibouti'));
insert into country(code, name) values('DM', i18n('Dominica'));
insert into country(code, name) values('DO', i18n('Dominican Republic'));
insert into country(code, name) values('TP', i18n('East Timor'));
insert into country(code, name) values('EC', i18n('Ecuador'));
insert into country(code, name) values('EG', i18n('Egypt'));
insert into country(code, name) values('SV', i18n('El Salvador'));
insert into country(code, name) values('GQ', i18n('Equatorial Guinea'));
insert into country(code, name) values('ER', i18n('Eritrea'));
insert into country(code, name) values('EE', i18n('Estonia'));
insert into country(code, name) values('ET', i18n('Ethiopia'));
insert into country(code, name) values('FK', i18n('Falkland Islands (Malvinas)'));
insert into country(code, name) values('FO', i18n('Faroe Islands'));
insert into country(code, name) values('FJ', i18n('Fiji'));
insert into country(code, name) values('FI', i18n('Finland'));
insert into country(code, name) values('FR', i18n('France'));
insert into country(code, name) values('GF', i18n('French Guiana'));
insert into country(code, name) values('PF', i18n('French Polynesia'));
insert into country(code, name) values('TF', i18n('French Southern Territories'));
insert into country(code, name) values('GA', i18n('Gabon'));
insert into country(code, name) values('GM', i18n('Gambia'));
insert into country(code, name) values('GE', i18n('Georgia'));
insert into country(code, name) values('DE', i18n('Germany'));
insert into country(code, name) values('GH', i18n('Ghana'));
insert into country(code, name) values('GI', i18n('Gibraltar'));
insert into country(code, name) values('GR', i18n('Greece'));
insert into country(code, name) values('GL', i18n('Greenland'));
insert into country(code, name) values('GD', i18n('Grenada'));
insert into country(code, name) values('GP', i18n('Guadeloupe'));
insert into country(code, name) values('GU', i18n('Guam'));
insert into country(code, name) values('GT', i18n('Guatemala'));
insert into country(code, name) values('GN', i18n('Guinea'));
insert into country(code, name) values('GW', i18n('Guinea-Bissau'));
insert into country(code, name) values('GY', i18n('Guyana'));
insert into country(code, name) values('HT', i18n('Haiti'));
insert into country(code, name) values('HM', i18n('Heard Island and McDonald Island'));
insert into country(code, name) values('VA', i18n('Holy See (Vatican City State)'));
insert into country(code, name) values('HN', i18n('Honduras'));
insert into country(code, name) values('HK', i18n('Hong Kong'));
insert into country(code, name) values('HU', i18n('Hungary'));
insert into country(code, name) values('IS', i18n('Iceland'));
insert into country(code, name) values('IN', i18n('India'));
insert into country(code, name) values('ID', i18n('Indonesia'));
insert into country(code, name) values('IR', i18n('Iran, Islamic Republic Of'));
insert into country(code, name) values('IQ', i18n('Iraq'));
insert into country(code, name) values('IE', i18n('Ireland'));
insert into country(code, name) values('IL', i18n('Israel'));
insert into country(code, name) values('IT', i18n('Italy'));
insert into country(code, name) values('JM', i18n('Jamaica'));
insert into country(code, name) values('JP', i18n('Japan'));
insert into country(code, name) values('JO', i18n('Jordan'));
insert into country(code, name) values('KZ', i18n('Kazakstan'));
insert into country(code, name) values('KE', i18n('Kenya'));
insert into country(code, name) values('KI', i18n('Kiribati'));
insert into country(code, name) values('KP', i18n('Korea, Democratic People''s Republic'));
insert into country(code, name) values('KR', i18n('Korea, Republic Of'));
insert into country(code, name) values('KW', i18n('Kuwait'));
insert into country(code, name) values('KG', i18n('Kyrgyzstan'));
insert into country(code, name) values('LA', i18n('Lao People''s Democratic Republic'));
insert into country(code, name) values('LV', i18n('Latvia'));
insert into country(code, name) values('LB', i18n('Lebanon'));
insert into country(code, name) values('LS', i18n('Lesotho'));
insert into country(code, name) values('LR', i18n('Liberia'));
insert into country(code, name) values('LY', i18n('Libyan Arab Jamahiriya'));
insert into country(code, name) values('LI', i18n('Liechtenstein'));
insert into country(code, name) values('LT', i18n('Lithuania'));
insert into country(code, name) values('LU', i18n('Luxembourg'));
insert into country(code, name) values('MO', i18n('Macau'));
insert into country(code, name) values('MK', i18n('Macedonia, The Former Yugoslav'));
insert into country(code, name) values('MG', i18n('Madagascar'));
insert into country(code, name) values('MW', i18n('Malawi'));
insert into country(code, name) values('MY', i18n('Malaysia'));
insert into country(code, name) values('MV', i18n('Maldives'));
insert into country(code, name) values('ML', i18n('Mali'));
insert into country(code, name) values('MT', i18n('Malta'));
insert into country(code, name) values('MH', i18n('Marshall Islands'));
insert into country(code, name) values('MQ', i18n('Martinique'));
insert into country(code, name) values('MR', i18n('Mauritania'));
insert into country(code, name) values('MU', i18n('Mauritius'));
insert into country(code, name) values('YT', i18n('Mayotte'));
insert into country(code, name) values('MX', i18n('Mexico'));
insert into country(code, name) values('FM', i18n('Micronesia, Federated States O'));
insert into country(code, name) values('MD', i18n('Moldova, Republic Of'));
insert into country(code, name) values('MC', i18n('Monaco'));
insert into country(code, name) values('MN', i18n('Mongolia'));
insert into country(code, name) values('MS', i18n('Montserrat'));
insert into country(code, name) values('MA', i18n('Morocco'));
insert into country(code, name) values('MZ', i18n('Mozambique'));
insert into country(code, name) values('MM', i18n('Myanmar'));
insert into country(code, name) values('NA', i18n('Namibia'));
insert into country(code, name) values('NR', i18n('Nauru'));
insert into country(code, name) values('NP', i18n('Nepal'));
insert into country(code, name) values('NL', i18n('Netherlands'));
insert into country(code, name) values('AN', i18n('Netherlands Antilles'));
insert into country(code, name) values('NC', i18n('New Caledonia'));
insert into country(code, name) values('NZ', i18n('New Zealand'));
insert into country(code, name) values('NI', i18n('Nicaragua'));
insert into country(code, name) values('NE', i18n('Niger'));
insert into country(code, name) values('NG', i18n('Nigeria'));
insert into country(code, name) values('NU', i18n('Niue'));
insert into country(code, name) values('NF', i18n('Norfolk Island'));
insert into country(code, name) values('MP', i18n('Northern Mariana Islands'));
insert into country(code, name) values('NO', i18n('Norway'));
insert into country(code, name) values('OM', i18n('Oman'));
insert into country(code, name) values('PK', i18n('Pakistan'));
insert into country(code, name) values('PW', i18n('Palau'));
insert into country(code, name) values('PS', i18n('Palestinian Territory, Occupie'));
insert into country(code, name) values('PA', i18n('Panama'));
insert into country(code, name) values('PG', i18n('Papua New Guinea'));
insert into country(code, name) values('PY', i18n('Paraguay'));
insert into country(code, name) values('PE', i18n('Peru'));
insert into country(code, name) values('PH', i18n('Philippines'));
insert into country(code, name) values('PN', i18n('Pitcairn'));
insert into country(code, name) values('PL', i18n('Poland'));
insert into country(code, name) values('PT', i18n('Portugal'));
insert into country(code, name) values('PR', i18n('Puerto Rico'));
insert into country(code, name) values('QA', i18n('Qatar'));
insert into country(code, name) values('RE', i18n('Reunion'));
insert into country(code, name) values('RO', i18n('Romania'));
insert into country(code, name) values('RU', i18n('Russian Federation'));
insert into country(code, name) values('RW', i18n('Rwanda'));
insert into country(code, name) values('SH', i18n('Saint Helena'));
insert into country(code, name) values('KN', i18n('Saint Kitts and Nevis'));
insert into country(code, name) values('LC', i18n('Saint Lucia'));
insert into country(code, name) values('PM', i18n('Saint Pierre and Miquelon'));
insert into country(code, name) values('VC', i18n('Saint Vincent and The Grenadin'));
insert into country(code, name) values('WS', i18n('Samoa'));
insert into country(code, name) values('SM', i18n('San Marino'));
insert into country(code, name) values('ST', i18n('Sao Tome and Principe'));
insert into country(code, name) values('SA', i18n('Saudi Arabia'));
insert into country(code, name) values('SN', i18n('Senegal'));
insert into country(code, name) values('SC', i18n('Seychelles'));
insert into country(code, name) values('SL', i18n('Sierra Leone'));
insert into country(code, name) values('SG', i18n('Singapore'));
insert into country(code, name) values('SK', i18n('Slovakia'));
insert into country(code, name) values('SI', i18n('Slovenia'));
insert into country(code, name) values('SB', i18n('Solomon Islands'));
insert into country(code, name) values('SO', i18n('Somalia'));
insert into country(code, name) values('ZA', i18n('South Africa'));
insert into country(code, name) values('GS', i18n('South Georgia and The South Sa'));
insert into country(code, name) values('ES', i18n('Spain'));
insert into country(code, name) values('LK', i18n('Sri Lanka'));
insert into country(code, name) values('SD', i18n('Sudan'));
insert into country(code, name) values('SR', i18n('Suriname'));
insert into country(code, name) values('SJ', i18n('Svalbard and Jan Mayen'));
insert into country(code, name) values('SZ', i18n('Swaziland'));
insert into country(code, name) values('SE', i18n('Sweden'));
insert into country(code, name) values('CH', i18n('Switzerland'));
insert into country(code, name) values('SY', i18n('Syrian Arab Republic'));
insert into country(code, name) values('TW', i18n('Taiwan, Province Of China'));
insert into country(code, name) values('TJ', i18n('Tajikistan'));
insert into country(code, name) values('TZ', i18n('Tanzania, United Republic Of'));
insert into country(code, name) values('TH', i18n('Thailand'));
insert into country(code, name) values('TG', i18n('Togo'));
insert into country(code, name) values('TK', i18n('Tokelau'));
insert into country(code, name) values('TO', i18n('Tonga'));
insert into country(code, name) values('TT', i18n('Trinidad and Tobago'));
insert into country(code, name) values('TN', i18n('Tunisia'));
insert into country(code, name) values('TR', i18n('Turkey'));
insert into country(code, name) values('TM', i18n('Turkmenistan'));
insert into country(code, name) values('TC', i18n('Turks and Caicos Islands'));
insert into country(code, name) values('TV', i18n('Tuvalu'));
insert into country(code, name) values('UG', i18n('Uganda'));
insert into country(code, name) values('UA', i18n('Ukraine'));
insert into country(code, name) values('AE', i18n('United Arab Emirates'));
insert into country(code, name) values('GB', i18n('United Kingdom'));
insert into country(code, name) values('US', i18n('United States'));

-- FIXME: move to it's own file
insert into state (code, country, name) values ('S', 'NZ', 'South Island');
insert into state (code, country, name) values ('N', 'NZ', 'North Island');

-- ===================================================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmDemographics-GIS-data.sql,v $', '$Revision: 1.6 $', False);

-- delete from gm_schema_revision where filename = '$RCSfile: gmDemographics-GIS-data.sql,v $';
-- INSERT INTO gm_schema_revision (filename, version, is_core) VALUES('$RCSfile: gmDemographics-GIS-data.sql,v $', '$Revision: 1.6 $', True);

-- ===================================================================
-- $Log: gmDemographics-GIS-data.sql,v $
-- Revision 1.6  2005-07-15 21:16:55  ncq
-- - add "dummy" states for NZ for now
--
-- Revision 1.5  2005/07/14 21:31:42  ncq
-- - partially use improved schema revision tracking
--
-- Revision 1.4  2005/05/04 08:56:55  ncq
-- - properly capsify country names
--
-- Revision 1.3  2004/02/27 07:05:30  ihaywood
-- org_address is dead. Doesn't make
-- sense for orgs to have multiple addresses IMHO
-- as we allow branch organisations
--
-- Revision 1.2  2003/12/29 15:32:59  uid66147
-- - remove begin/commit as it does not play well with transactions in python
--
-- Revision 1.1  2003/08/02 10:41:29  ncq
-- - rearranging files for clarity as to services/schemata
--
-- Revision 1.4  2003/05/12 12:43:39  ncq
-- - gmI18N, gmServices and gmSchemaRevision are imported globally at the
--   database level now, don't include them in individual schema file anymore
--
-- Revision 1.3  2003/03/24 10:45:12  ncq
-- - country codes moved to GisData
-- - added constraint on table urb
--
-- Revision 1.2  2003/03/24 10:41:16  ncq
-- - added ISO country codes
--
-- Revision 1.1  2003/02/14 10:46:17  ncq
-- - breaking out enumeration data
--
