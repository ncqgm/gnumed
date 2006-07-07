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
INSERT into dem.address_type(id, name) values(1, i18n.i18n('home'));
INSERT into dem.address_type(id, name) values(2, i18n.i18n('work'));
INSERT into dem.address_type(id, name) values(3, i18n.i18n('parents'));
INSERT into dem.address_type(id, name) values(4, i18n.i18n('holidays'));
INSERT into dem.address_type(id, name) values(5, i18n.i18n('temporary'));

-- comms types. Don't change ID numbers

insert into dem.enum_comm_types (id, description) values (1, i18n.i18n('email'));
insert into dem.enum_comm_types (id, description) values (2, i18n.i18n('fax'));
insert into dem.enum_comm_types (id, description) values (3, i18n.i18n('homephone'));
insert into dem.enum_comm_types (id, description) values (4, i18n.i18n('workphone'));
insert into dem.enum_comm_types (id, description) values (5, i18n.i18n('mobile'));
insert into dem.enum_comm_types (id, description) values (6, i18n.i18n('web'));
insert into dem.enum_comm_types (id, description) values (7, i18n.i18n('jabber'));

-- external ID types
insert into dem.enum_ext_id_types (name, issuer, context) values ('oscar_demographic_no', 'Syan Tan', 'p');

-- ===================================================================
-- here come the ISO country codes ...

insert into dem.country(code, name) values('AF', i18n.i18n('Afghanistan'));
insert into dem.country(code, name) values('AL', i18n.i18n('Albania'));
insert into dem.country(code, name) values('DZ', i18n.i18n('Algeria'));
insert into dem.country(code, name) values('AS', i18n.i18n('American Samoa'));
insert into dem.country(code, name) values('AD', i18n.i18n('Andorra'));
insert into dem.country(code, name) values('AO', i18n.i18n('Angola'));
insert into dem.country(code, name) values('AI', i18n.i18n('Anguilla'));
insert into dem.country(code, name) values('AQ', i18n.i18n('Antarctica'));
insert into dem.country(code, name) values('AG', i18n.i18n('Antigua and Barbuda'));
insert into dem.country(code, name) values('AR', i18n.i18n('Argentina'));
insert into dem.country(code, name) values('AM', i18n.i18n('Armenia'));
insert into dem.country(code, name) values('AW', i18n.i18n('Aruba'));
insert into dem.country(code, name) values('AU', i18n.i18n('Australia'));
insert into dem.country(code, name) values('AT', i18n.i18n('Austria'));
insert into dem.country(code, name) values('AZ', i18n.i18n('Azerbaijan'));
insert into dem.country(code, name) values('BS', i18n.i18n('Bahamas'));
insert into dem.country(code, name) values('BH', i18n.i18n('Bahrain'));
insert into dem.country(code, name) values('BD', i18n.i18n('Bangladesh'));
insert into dem.country(code, name) values('BB', i18n.i18n('Barbados'));
insert into dem.country(code, name) values('BY', i18n.i18n('Belarus'));
insert into dem.country(code, name) values('BE', i18n.i18n('Belgium'));
insert into dem.country(code, name) values('BZ', i18n.i18n('Belize'));
insert into dem.country(code, name) values('BJ', i18n.i18n('Benin'));
insert into dem.country(code, name) values('BM', i18n.i18n('Bermuda'));
insert into dem.country(code, name) values('BT', i18n.i18n('Bhutan'));
insert into dem.country(code, name) values('BO', i18n.i18n('Bolivia'));
insert into dem.country(code, name) values('BA', i18n.i18n('Bosnia and Herzegovina'));
insert into dem.country(code, name) values('BW', i18n.i18n('Botswana'));
insert into dem.country(code, name) values('BV', i18n.i18n('Bouvet Island'));
insert into dem.country(code, name) values('BR', i18n.i18n('Brazil'));
insert into dem.country(code, name) values('IO', i18n.i18n('British Indian Ocean Territory'));
insert into dem.country(code, name) values('BN', i18n.i18n('Brunei Darussalam'));
insert into dem.country(code, name) values('BG', i18n.i18n('Bulgaria'));
insert into dem.country(code, name) values('BF', i18n.i18n('Burkina Faso'));
insert into dem.country(code, name) values('BI', i18n.i18n('Burundi'));
insert into dem.country(code, name) values('KH', i18n.i18n('Cambodia'));
insert into dem.country(code, name) values('CM', i18n.i18n('Cameroon'));
insert into dem.country(code, name) values('CA', i18n.i18n('Canada'));
insert into dem.country(code, name) values('CV', i18n.i18n('Cape Verde'));
insert into dem.country(code, name) values('KY', i18n.i18n('Cayman Islands'));
insert into dem.country(code, name) values('CF', i18n.i18n('Central African Republic'));
insert into dem.country(code, name) values('TD', i18n.i18n('Chad'));
insert into dem.country(code, name) values('CL', i18n.i18n('Chile'));
insert into dem.country(code, name) values('CN', i18n.i18n('China'));
insert into dem.country(code, name) values('CX', i18n.i18n('Christmas Island'));
insert into dem.country(code, name) values('CC', i18n.i18n('Cocos (Keeling) Islands'));
insert into dem.country(code, name) values('CO', i18n.i18n('Colombia'));
insert into dem.country(code, name) values('KM', i18n.i18n('Comoros'));
insert into dem.country(code, name) values('CG', i18n.i18n('Congo'));
insert into dem.country(code, name) values('CD', i18n.i18n('Congo, The Democratic Republic'));
insert into dem.country(code, name) values('CK', i18n.i18n('Cook Islands'));
insert into dem.country(code, name) values('CR', i18n.i18n('Costa Rica'));
insert into dem.country(code, name) values('CI', i18n.i18n('Cote D''Ivoire'));
insert into dem.country(code, name) values('HR', i18n.i18n('Croatia'));
insert into dem.country(code, name) values('CU', i18n.i18n('Cuba'));
insert into dem.country(code, name) values('CY', i18n.i18n('Cyprus'));
insert into dem.country(code, name) values('CZ', i18n.i18n('Czech Republic'));
insert into dem.country(code, name) values('DK', i18n.i18n('Denmark'));
insert into dem.country(code, name) values('DJ', i18n.i18n('Djibouti'));
insert into dem.country(code, name) values('DM', i18n.i18n('Dominica'));
insert into dem.country(code, name) values('DO', i18n.i18n('Dominican Republic'));
insert into dem.country(code, name) values('TP', i18n.i18n('East Timor'));
insert into dem.country(code, name) values('EC', i18n.i18n('Ecuador'));
insert into dem.country(code, name) values('EG', i18n.i18n('Egypt'));
insert into dem.country(code, name) values('SV', i18n.i18n('El Salvador'));
insert into dem.country(code, name) values('GQ', i18n.i18n('Equatorial Guinea'));
insert into dem.country(code, name) values('ER', i18n.i18n('Eritrea'));
insert into dem.country(code, name) values('EE', i18n.i18n('Estonia'));
insert into dem.country(code, name) values('ET', i18n.i18n('Ethiopia'));
insert into dem.country(code, name) values('FK', i18n.i18n('Falkland Islands (Malvinas)'));
insert into dem.country(code, name) values('FO', i18n.i18n('Faroe Islands'));
insert into dem.country(code, name) values('FJ', i18n.i18n('Fiji'));
insert into dem.country(code, name) values('FI', i18n.i18n('Finland'));
insert into dem.country(code, name) values('FR', i18n.i18n('France'));
insert into dem.country(code, name) values('GF', i18n.i18n('French Guiana'));
insert into dem.country(code, name) values('PF', i18n.i18n('French Polynesia'));
insert into dem.country(code, name) values('TF', i18n.i18n('French Southern Territories'));
insert into dem.country(code, name) values('GA', i18n.i18n('Gabon'));
insert into dem.country(code, name) values('GM', i18n.i18n('Gambia'));
insert into dem.country(code, name) values('GE', i18n.i18n('Georgia'));
insert into dem.country(code, name) values('DE', i18n.i18n('Germany'));
insert into dem.country(code, name) values('GH', i18n.i18n('Ghana'));
insert into dem.country(code, name) values('GI', i18n.i18n('Gibraltar'));
insert into dem.country(code, name) values('GR', i18n.i18n('Greece'));
insert into dem.country(code, name) values('GL', i18n.i18n('Greenland'));
insert into dem.country(code, name) values('GD', i18n.i18n('Grenada'));
insert into dem.country(code, name) values('GP', i18n.i18n('Guadeloupe'));
insert into dem.country(code, name) values('GU', i18n.i18n('Guam'));
insert into dem.country(code, name) values('GT', i18n.i18n('Guatemala'));
insert into dem.country(code, name) values('GN', i18n.i18n('Guinea'));
insert into dem.country(code, name) values('GW', i18n.i18n('Guinea-Bissau'));
insert into dem.country(code, name) values('GY', i18n.i18n('Guyana'));
insert into dem.country(code, name) values('HT', i18n.i18n('Haiti'));
insert into dem.country(code, name) values('HM', i18n.i18n('Heard Island and McDonald Island'));
insert into dem.country(code, name) values('VA', i18n.i18n('Holy See (Vatican City State)'));
insert into dem.country(code, name) values('HN', i18n.i18n('Honduras'));
insert into dem.country(code, name) values('HK', i18n.i18n('Hong Kong'));
insert into dem.country(code, name) values('HU', i18n.i18n('Hungary'));
insert into dem.country(code, name) values('IS', i18n.i18n('Iceland'));
insert into dem.country(code, name) values('IN', i18n.i18n('India'));
insert into dem.country(code, name) values('ID', i18n.i18n('Indonesia'));
insert into dem.country(code, name) values('IR', i18n.i18n('Iran, Islamic Republic Of'));
insert into dem.country(code, name) values('IQ', i18n.i18n('Iraq'));
insert into dem.country(code, name) values('IE', i18n.i18n('Ireland'));
insert into dem.country(code, name) values('IL', i18n.i18n('Israel'));
insert into dem.country(code, name) values('IT', i18n.i18n('Italy'));
insert into dem.country(code, name) values('JM', i18n.i18n('Jamaica'));
insert into dem.country(code, name) values('JP', i18n.i18n('Japan'));
insert into dem.country(code, name) values('JO', i18n.i18n('Jordan'));
insert into dem.country(code, name) values('KZ', i18n.i18n('Kazakstan'));
insert into dem.country(code, name) values('KE', i18n.i18n('Kenya'));
insert into dem.country(code, name) values('KI', i18n.i18n('Kiribati'));
insert into dem.country(code, name) values('KP', i18n.i18n('Korea, Democratic People''s Republic'));
insert into dem.country(code, name) values('KR', i18n.i18n('Korea, Republic Of'));
insert into dem.country(code, name) values('KW', i18n.i18n('Kuwait'));
insert into dem.country(code, name) values('KG', i18n.i18n('Kyrgyzstan'));
insert into dem.country(code, name) values('LA', i18n.i18n('Lao People''s Democratic Republic'));
insert into dem.country(code, name) values('LV', i18n.i18n('Latvia'));
insert into dem.country(code, name) values('LB', i18n.i18n('Lebanon'));
insert into dem.country(code, name) values('LS', i18n.i18n('Lesotho'));
insert into dem.country(code, name) values('LR', i18n.i18n('Liberia'));
insert into dem.country(code, name) values('LY', i18n.i18n('Libyan Arab Jamahiriya'));
insert into dem.country(code, name) values('LI', i18n.i18n('Liechtenstein'));
insert into dem.country(code, name) values('LT', i18n.i18n('Lithuania'));
insert into dem.country(code, name) values('LU', i18n.i18n('Luxembourg'));
insert into dem.country(code, name) values('MO', i18n.i18n('Macau'));
insert into dem.country(code, name) values('MK', i18n.i18n('Macedonia, The Former Yugoslav'));
insert into dem.country(code, name) values('MG', i18n.i18n('Madagascar'));
insert into dem.country(code, name) values('MW', i18n.i18n('Malawi'));
insert into dem.country(code, name) values('MY', i18n.i18n('Malaysia'));
insert into dem.country(code, name) values('MV', i18n.i18n('Maldives'));
insert into dem.country(code, name) values('ML', i18n.i18n('Mali'));
insert into dem.country(code, name) values('MT', i18n.i18n('Malta'));
insert into dem.country(code, name) values('MH', i18n.i18n('Marshall Islands'));
insert into dem.country(code, name) values('MQ', i18n.i18n('Martinique'));
insert into dem.country(code, name) values('MR', i18n.i18n('Mauritania'));
insert into dem.country(code, name) values('MU', i18n.i18n('Mauritius'));
insert into dem.country(code, name) values('YT', i18n.i18n('Mayotte'));
insert into dem.country(code, name) values('MX', i18n.i18n('Mexico'));
insert into dem.country(code, name) values('FM', i18n.i18n('Micronesia, Federated States O'));
insert into dem.country(code, name) values('MD', i18n.i18n('Moldova, Republic Of'));
insert into dem.country(code, name) values('MC', i18n.i18n('Monaco'));
insert into dem.country(code, name) values('MN', i18n.i18n('Mongolia'));
insert into dem.country(code, name) values('MS', i18n.i18n('Montserrat'));
insert into dem.country(code, name) values('MA', i18n.i18n('Morocco'));
insert into dem.country(code, name) values('MZ', i18n.i18n('Mozambique'));
insert into dem.country(code, name) values('MM', i18n.i18n('Myanmar'));
insert into dem.country(code, name) values('NA', i18n.i18n('Namibia'));
insert into dem.country(code, name) values('NR', i18n.i18n('Nauru'));
insert into dem.country(code, name) values('NP', i18n.i18n('Nepal'));
insert into dem.country(code, name) values('NL', i18n.i18n('Netherlands'));
insert into dem.country(code, name) values('AN', i18n.i18n('Netherlands Antilles'));
insert into dem.country(code, name) values('NC', i18n.i18n('New Caledonia'));
insert into dem.country(code, name) values('NZ', i18n.i18n('New Zealand'));
insert into dem.country(code, name) values('NI', i18n.i18n('Nicaragua'));
insert into dem.country(code, name) values('NE', i18n.i18n('Niger'));
insert into dem.country(code, name) values('NG', i18n.i18n('Nigeria'));
insert into dem.country(code, name) values('NU', i18n.i18n('Niue'));
insert into dem.country(code, name) values('NF', i18n.i18n('Norfolk Island'));
insert into dem.country(code, name) values('MP', i18n.i18n('Northern Mariana Islands'));
insert into dem.country(code, name) values('NO', i18n.i18n('Norway'));
insert into dem.country(code, name) values('OM', i18n.i18n('Oman'));
insert into dem.country(code, name) values('PK', i18n.i18n('Pakistan'));
insert into dem.country(code, name) values('PW', i18n.i18n('Palau'));
insert into dem.country(code, name) values('PS', i18n.i18n('Palestinian Territory, Occupie'));
insert into dem.country(code, name) values('PA', i18n.i18n('Panama'));
insert into dem.country(code, name) values('PG', i18n.i18n('Papua New Guinea'));
insert into dem.country(code, name) values('PY', i18n.i18n('Paraguay'));
insert into dem.country(code, name) values('PE', i18n.i18n('Peru'));
insert into dem.country(code, name) values('PH', i18n.i18n('Philippines'));
insert into dem.country(code, name) values('PN', i18n.i18n('Pitcairn'));
insert into dem.country(code, name) values('PL', i18n.i18n('Poland'));
insert into dem.country(code, name) values('PT', i18n.i18n('Portugal'));
insert into dem.country(code, name) values('PR', i18n.i18n('Puerto Rico'));
insert into dem.country(code, name) values('QA', i18n.i18n('Qatar'));
insert into dem.country(code, name) values('RE', i18n.i18n('Reunion'));
insert into dem.country(code, name) values('RO', i18n.i18n('Romania'));
insert into dem.country(code, name) values('RU', i18n.i18n('Russian Federation'));
insert into dem.country(code, name) values('RW', i18n.i18n('Rwanda'));
insert into dem.country(code, name) values('SH', i18n.i18n('Saint Helena'));
insert into dem.country(code, name) values('KN', i18n.i18n('Saint Kitts and Nevis'));
insert into dem.country(code, name) values('LC', i18n.i18n('Saint Lucia'));
insert into dem.country(code, name) values('PM', i18n.i18n('Saint Pierre and Miquelon'));
insert into dem.country(code, name) values('VC', i18n.i18n('Saint Vincent and The Grenadin'));
insert into dem.country(code, name) values('WS', i18n.i18n('Samoa'));
insert into dem.country(code, name) values('SM', i18n.i18n('San Marino'));
insert into dem.country(code, name) values('ST', i18n.i18n('Sao Tome and Principe'));
insert into dem.country(code, name) values('SA', i18n.i18n('Saudi Arabia'));
insert into dem.country(code, name) values('SN', i18n.i18n('Senegal'));
insert into dem.country(code, name) values('SC', i18n.i18n('Seychelles'));
insert into dem.country(code, name) values('SL', i18n.i18n('Sierra Leone'));
insert into dem.country(code, name) values('SG', i18n.i18n('Singapore'));
insert into dem.country(code, name) values('SK', i18n.i18n('Slovakia'));
insert into dem.country(code, name) values('SI', i18n.i18n('Slovenia'));
insert into dem.country(code, name) values('SB', i18n.i18n('Solomon Islands'));
insert into dem.country(code, name) values('SO', i18n.i18n('Somalia'));
insert into dem.country(code, name) values('ZA', i18n.i18n('South Africa'));
insert into dem.country(code, name) values('GS', i18n.i18n('South Georgia and The South Sa'));
insert into dem.country(code, name) values('ES', i18n.i18n('Spain'));
insert into dem.country(code, name) values('LK', i18n.i18n('Sri Lanka'));
insert into dem.country(code, name) values('SD', i18n.i18n('Sudan'));
insert into dem.country(code, name) values('SR', i18n.i18n('Suriname'));
insert into dem.country(code, name) values('SJ', i18n.i18n('Svalbard and Jan Mayen'));
insert into dem.country(code, name) values('SZ', i18n.i18n('Swaziland'));
insert into dem.country(code, name) values('SE', i18n.i18n('Sweden'));
insert into dem.country(code, name) values('CH', i18n.i18n('Switzerland'));
insert into dem.country(code, name) values('SY', i18n.i18n('Syrian Arab Republic'));
insert into dem.country(code, name) values('TW', i18n.i18n('Taiwan, Province Of China'));
insert into dem.country(code, name) values('TJ', i18n.i18n('Tajikistan'));
insert into dem.country(code, name) values('TZ', i18n.i18n('Tanzania, United Republic Of'));
insert into dem.country(code, name) values('TH', i18n.i18n('Thailand'));
insert into dem.country(code, name) values('TG', i18n.i18n('Togo'));
insert into dem.country(code, name) values('TK', i18n.i18n('Tokelau'));
insert into dem.country(code, name) values('TO', i18n.i18n('Tonga'));
insert into dem.country(code, name) values('TT', i18n.i18n('Trinidad and Tobago'));
insert into dem.country(code, name) values('TN', i18n.i18n('Tunisia'));
insert into dem.country(code, name) values('TR', i18n.i18n('Turkey'));
insert into dem.country(code, name) values('TM', i18n.i18n('Turkmenistan'));
insert into dem.country(code, name) values('TC', i18n.i18n('Turks and Caicos Islands'));
insert into dem.country(code, name) values('TV', i18n.i18n('Tuvalu'));
insert into dem.country(code, name) values('UG', i18n.i18n('Uganda'));
insert into dem.country(code, name) values('UA', i18n.i18n('Ukraine'));
insert into dem.country(code, name) values('AE', i18n.i18n('United Arab Emirates'));
insert into dem.country(code, name) values('GB', i18n.i18n('United Kingdom'));
insert into dem.country(code, name) values('US', i18n.i18n('United States'));


-- ===================================================================
-- do simple schema revision tracking
select log_script_insertion('$RCSfile: gmDemographics-GIS-data.sql,v $', '$Revision: 1.12 $');

-- ===================================================================
-- $Log: gmDemographics-GIS-data.sql,v $
-- Revision 1.12  2006-07-07 09:08:31  ncq
-- - add "oscar_demographic_no" to external ID types
--
-- Revision 1.11  2006/01/10 12:58:17  sjtan
--
-- path for plpgsql on a debian system added; remove need to know base sql dir for gmCountryCodes.sql
--
-- Revision 1.10  2006/01/09 12:41:46  ncq
-- - lots of i18n.i18n()
--
-- Revision 1.9  2006/01/06 10:12:02  ncq
-- - add missing grants
-- - add_table_for_audit() now in "audit" schema
-- - demographics now in "dem" schema
-- - add view v_inds4vaccine
-- - move staff_role from clinical into demographics
-- - put add_coded_term() into "clin" schema
-- - put German things into "de_de" schema
--
-- Revision 1.8  2005/09/25 17:47:49  ncq
-- - include state data
--
-- Revision 1.7  2005/09/19 16:38:51  ncq
-- - adjust to removed is_core from gm_schema_revision
--
-- Revision 1.6  2005/07/15 21:16:55  ncq
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
