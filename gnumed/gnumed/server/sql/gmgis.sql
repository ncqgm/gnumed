-- project: GNUMed
-- database: GIS
-- purpose:  geographic information (mostly of type 'address')
-- author: hherb
-- copyright: Dr. Horst Herb, horst@hherb.com
-- license: GPL (details at http://gnu.org)
-- version: 0.4
-- changelog:
-- 17.11.2001:  (hherb) first useable version
-- 04.03.2002:  (hherb) address_type bug in view basic_addess fixed
-- 04.03.2002:  (hherb) table state constraint added
-- 08.03.2002:  (ihaywood) rules for v_basic_address, address_info altered
-- 30.03.2002:  (hherb) view basic_address renamed to v_basic_address
--               bugfix in rule update_address
--               bugfix in rule insert_address
-- 31.03.2002:  rules for v_basic_address rewritten, using id now
--               and supporting external reference counting


--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


-- any table that needs auditing MUST inherit audit_gis
-- A python script (gmhistorian.py) generates automatically all triggers
-- and tables neccessary to allow versioning and audit trail keeping of
-- these tables

create table audit_gis (
        audit_id serial primary key
);

COMMENT ON TABLE audit_gis IS
'not for direct use - must be inherited by all auditable tables';

-- country codes as per ISO 3166-1
-- no versioning / check sum neccessary, as this table
-- only uses original ISO data (= reference verifiable any time)

create table country (
        code char(2) unique primary key,
        name varchar(80),
        deprecated date default NULL
);

COMMENT ON TABLE country IS
'a countries name and international code';

COMMENT ON COLUMN country.code IS
'international two character country code as per ISO 3166-1';

COMMENT ON COLUMN country.deprecated IS
'date when this country ceased officially to exist (if applicable)';


--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


-- state codes. Any need for more than 3 characters?
-- yes, at least in Germany we have up to 6

create table state (
        id serial primary key,
        code char(10),
        country char(2) references country(code),
        name varchar(60),
        deprecated date,
        constraint nodupes UNIQUE (code, country)
) inherits (audit_gis);

COMMENT ON TABLE state IS
'state codes (country specific)';

COMMENT ON COLUMN state.code IS
'state code';

COMMENT ON COLUMN state.country IS
'2 character ISO 3166-1 country code';

COMMENT ON COLUMN country.deprecated IS
'date when this state ceased officially to exist (if applicable)';


--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


create table urb (
        id serial primary key,
        statecode int references state(id),
        postcode char(8), 
	-- this does not work in the UK! Seperate postcodes for each street
        name varchar(60)
) inherits (audit_gis);

COMMENT ON TABLE urb IS
'cities, towns, dwellings ...';

COMMENT ON COLUMN urb.statecode IS
'reference to information about country and state';

COMMENT ON COLUMN urb.postcode IS
'the postcode (if applicable';

COMMENT ON COLUMN urb.name IS
'the name of the city/town/dwelling';


--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


create table street (
        id serial primary key,
        id_urb integer references urb not null,
        name varchar(60),
	postcode char (10) -- for UK (or similar) postcodes
) inherits (audit_gis);

COMMENT ON TABLE street IS
'street names, specific for distinct "urbs"';

COMMENT ON COLUMN street.id_urb IS
'reference to information postcode, city, country and state';

COMMENT ON COLUMN street.name IS
'name of this street';

COMMENT ON COLUMN street.postcode IS
'postcode for systems (such as UK Royal Mail) which specify the street.';


--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


create table address_type (
        id serial primary key,
        name char(10) NOT NULL
) inherits (audit_gis);


INSERT INTO address_type(id, name) values(1,'home'); -- do not alter the id of home !
INSERT INTO address_type(id, name) values(2,'work');
INSERT INTO address_type(id, name) values(3,'parents');
INSERT INTO address_type(id, name) values(4,'holidays');
INSERT INTO address_type(id, name) values(5,'temporary');


--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


create table address (
        id serial primary key,
        street int references street(id),
        number char(10),
        addendum text
) inherits (audit_gis);


--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-- Other databases may reference to an address stored in this table.
-- As Postgres does not allow (yet) cross database queries, we use
-- external reference tables containing "external reference" counters
-- in order to preserve referential integrity
-- (no address shall be deleted as long as there is an external object
-- referencing this address)

create table address_external_ref (
        id int references address primary key,
        refcounter int default 0
);


--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


-- finds the state for a given postcode in a given country
DROP function find_state(text, text);
CREATE FUNCTION find_state (text, text) RETURNS text AS '
DECLARE
        pcode ALIAS FOR $1;	-- post code
	ccode ALIAS FOR $2;	-- country code
        s RECORD;
	retval text := NULL;
BEGIN
        SELECT INTO s * FROM state WHERE id =
	(SELECT statecode from urb where postcode like pcode||''%'' limit 1)
	AND country=ccode;
        IF FOUND THEN
           retval := s.code;
        END IF;
	RETURN retval;
END;' LANGUAGE 'plpgsql';


--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
create table identities_addresses (
        id serial primary key,
        id_identity integer references identity,
        id_address integer references address,
        id_type int references address_type default 1,
	address_source varchar(30)
) inherits (audit_identity);

COMMENT ON TABLE identities_addresses IS
'a many-to-many pivot table linking addresses to identities';

COMMENT ON COLUMN identities_addresses.id_identity IS
'identity to whom the address belongs';

COMMENT ON COLUMN identities_addresses.id_address IS
'address belonging to this identity';

COMMENT ON COLUMN identities_addresses.id_type IS
'type of this address (like home, work, parents, holidays ...)';


create view v_basic_address as
-- if you suffer from performance problems when selecting from this view,
-- implement it as a real table and create rules / triggers for insert,
-- update and delete that will update the underlying tables accordingly
select
	a.id as addr_id,
        s.country as country,
        s.code as state,
        u.postcode as postcode,
        u.name as city,
        a.number as number,
        str.name as street,
        a.addendum as street2  ,
 	t.name as address_at

from
        address a,
        state s,
        urb u,
        street str  ,
	address_type t
where
        a.street = str.id
        and
        str.id_urb = u.id
        and
        u.statecode = s.id;

-- added IH 8/3/02
-- insert, delete, and update rules on this table
-- problem: the street table had better contain the street.
-- solution: function to auto-create street records on demand.


--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


-- This function returns the id of street, BUT if the street does not
-- exist, it is created.
drop function find_street(text, integer);
CREATE FUNCTION find_street (text, integer) RETURNS integer AS '
DECLARE
        s_name ALIAS FOR $1;
        s_id_urb ALIAS FOR $2;
        s RECORD;
BEGIN
        SELECT INTO s * FROM street WHERE name = s_name AND
               id_urb = s_id_urb;
        IF FOUND THEN
           RETURN s.id;
        ELSE
           INSERT INTO street (id_urb, name) VALUES (s_id_urb, s_name);
           RETURN currval (''street_id_seq'');
        END IF;
END;' LANGUAGE 'plpgsql';


-- This function returns the id of a state, BUT if the state does not
-- exist, it is created.
drop function find_or_create_state(text, text);
CREATE FUNCTION find_or_create_state(text, text) RETURNS integer AS '
DECLARE
        s_code ALIAS FOR $1;
        s_country ALIAS FOR $2;
        s RECORD;
BEGIN
        SELECT INTO s * FROM state 
	WHERE code = s_code
	AND country = s_country;
        IF FOUND THEN
           RETURN s.id;
        ELSE
           INSERT INTO state (code, country) VALUES (s_code, s_country);
           RETURN currval (''state_id_seq'');
        END IF;
END;' LANGUAGE 'plpgsql';



-- This function returns the id of urb, BUT if the urb does not
-- exist, it is created.
drop function find_urb(text, text, text, text);
CREATE FUNCTION find_urb (text, text, text, text) RETURNS integer AS '
DECLARE
        u_country ALIAS FOR $1;
        u_state ALIAS FOR $2;
	u_postcode ALIAS FOR $3;
        u_name ALIAS FOR $4;
        u RECORD;
	state_code INTEGER;
BEGIN
	state_code = find_or_create_state(u_state, u_country);
	SELECT INTO u * FROM urb
	WHERE statecode = statecode
	AND postcode = u_postcode
	AND name = u_name;

        IF FOUND THEN
           RETURN u.id;
        ELSE
           INSERT INTO urb (statecode, postcode, name)
	   VALUES (state_code, u_postcode, u_name);
           RETURN currval (''urb_id_seq'');
        END IF;
END;' LANGUAGE 'plpgsql';


--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

drop rule insert_address;

CREATE RULE insert_address AS ON INSERT TO v_basic_address DO INSTEAD
        INSERT INTO address (street, number, addendum)
        VALUES (find_street (NEW.street, 
	                      find_urb(NEW.country, NEW.state, NEW.postcode, NEW.city)),
                NEW.number,
	        NEW.street2);

--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

CREATE RULE delete_address AS ON DELETE TO v_basic_address DO INSTEAD
	DELETE FROM address
	WHERE address.id = OLD.addr_id;


--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-- updates the basic address data as identified by it's unique id

CREATE RULE update_address AS ON UPDATE TO v_basic_address DO INSTEAD
       UPDATE address
       SET number = NEW.number, addendum = NEW.street2,
       street = find_street (NEW.street,
                  (SELECT urb.id FROM urb, state WHERE
                   urb.name = NEW.city AND
                   urb.postcode = NEW.postcode AND
                   urb.statecode = state.id AND
                   state.code = NEW.state AND
                   state.country = NEW.country))
        WHERE
               address.id=OLD.addr_id;

-- =============================================

-- the following table still needs a lot of work.
-- especially the GPS and map related information needs to be
-- normalized

-- added IH 8/3/02
-- table for street civilian type maps, i.e Melways
create table mapbook (
       id serial,
       name char (30)
);


--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


-- table for co-ordinate systems, such at latitude-longitude
-- there are others, military, aviation and country-specific.
-- GPS handsets can display several.
create table coordinate (
      id serial,
      name varchar (30),
      scale float
      -- NOTE: this converts distances from the co-ordinate units to
      -- kilometres.
      -- theoretically this may be problematic with some systems due to the
      -- ellipsoid nature of the Earth, but in reality it is unlikely to matter
);


--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


create table address_info (
        address_id int references address(id),
        location point,
-- this refers to a SQL point type. This would allow us to do
-- interesting queries, like, how many patients live within
-- 10kms of the clinic.
        id_coord integer references coordinate (id),
        mapref char(30),
        id_map integer references mapbook (id),
        howto_get_there text,
        comments text
) inherits (audit_gis);


--~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


-- Here come the ISO country codes ...
COPY country FROM stdin;
AF	AFGHANISTAN	\N
AL	ALBANIA	\N
DZ	ALGERIA	\N
AS	AMERICAN SAMOA	\N
AD	ANDORRA	\N
AO	ANGOLA	\N
AI	ANGUILLA	\N
AQ	ANTARCTICA	\N
AG	ANTIGUA AND BARBUDA	\N
AR	ARGENTINA	\N
AM	ARMENIA	\N
AW	ARUBA	\N
AU	AUSTRALIA	\N
AT	AUSTRIA	\N
AZ	AZERBAIJAN	\N
BS	BAHAMAS	\N
BH	BAHRAIN	\N
BD	BANGLADESH	\N
BB	BARBADOS	\N
BY	BELARUS	\N
BE	BELGIUM	\N
BZ	BELIZE	\N
BJ	BENIN	\N
BM	BERMUDA	\N
BT	BHUTAN	\N
BO	BOLIVIA	\N
BA	BOSNIA AND HERZEGOVINA	\N
BW	BOTSWANA	\N
BV	BOUVET ISLAND	\N
BR	BRAZIL	\N
IO	BRITISH INDIAN OCEAN TERRITORY	\N
BN	BRUNEI DARUSSALAM	\N
BG	BULGARIA	\N
BF	BURKINA FASO	\N
BI	BURUNDI	\N
KH	CAMBODIA	\N
CM	CAMEROON	\N
CA	CANADA	\N
CV	CAPE VERDE	\N
KY	CAYMAN ISLANDS	\N
CF	CENTRAL AFRICAN REPUBLIC	\N
TD	CHAD	\N
CL	CHILE	\N
CN	CHINA	\N
CX	CHRISTMAS ISLAND	\N
CC	COCOS (KEELING) ISLANDS	\N
CO	COLOMBIA	\N
KM	COMOROS	\N
CG	CONGO	\N
CD	CONGO, THE DEMOCRATIC REPUBLIC	\N
CK	COOK ISLANDS	\N
CR	COSTA RICA	\N
CI	COTE D'IVOIRE	\N
HR	CROATIA	\N
CU	CUBA	\N
CY	CYPRUS	\N
CZ	CZECH REPUBLIC	\N
DK	DENMARK	\N
DJ	DJIBOUTI	\N
DM	DOMINICA	\N
DO	DOMINICAN REPUBLIC	\N
TP	EAST TIMOR	\N
EC	ECUADOR	\N
EG	EGYPT	\N
SV	EL SALVADOR	\N
GQ	EQUATORIAL GUINEA	\N
ER	ERITREA	\N
EE	ESTONIA	\N
ET	ETHIOPIA	\N
FK	FALKLAND ISLANDS (MALVINAS)	\N
FO	FAROE ISLANDS	\N
FJ	FIJI	\N
FI	FINLAND	\N
FR	FRANCE	\N
GF	FRENCH GUIANA	\N
PF	FRENCH POLYNESIA	\N
TF	FRENCH SOUTHERN TERRITORIES	\N
GA	GABON	\N
GM	GAMBIA	\N
GE	GEORGIA	\N
DE	GERMANY	\N
GH	GHANA	\N
GI	GIBRALTAR	\N
GR	GREECE	\N
GL	GREENLAND	\N
GD	GRENADA	\N
GP	GUADELOUPE	\N
GU	GUAM	\N
GT	GUATEMALA	\N
GN	GUINEA	\N
GW	GUINEA-BISSAU	\N
GY	GUYANA	\N
HT	HAITI	\N
HM	HEARD ISLAND AND MCDONALD ISLA	\N
VA	HOLY SEE (VATICAN CITY STATE)	\N
HN	HONDURAS	\N
HK	HONG KONG	\N
HU	HUNGARY	\N
IS	ICELAND	\N
IN	INDIA	\N
ID	INDONESIA	\N
IR	IRAN, ISLAMIC REPUBLIC OF	\N
IQ	IRAQ	\N
IE	IRELAND	\N
IL	ISRAEL	\N
IT	ITALY	\N
JM	JAMAICA	\N
JP	JAPAN	\N
JO	JORDAN	\N
KZ	KAZAKSTAN	\N
KE	KENYA	\N
KI	KIRIBATI	\N
KP	KOREA, DEMOCRATIC PEOPLE'S REP	\N
KR	KOREA, REPUBLIC OF	\N
KW	KUWAIT	\N
KG	KYRGYZSTAN	\N
LA	LAO PEOPLE'S DEMOCRATIC REPUBL	\N
LV	LATVIA	\N
LB	LEBANON	\N
LS	LESOTHO	\N
LR	LIBERIA	\N
LY	LIBYAN ARAB JAMAHIRIYA	\N
LI	LIECHTENSTEIN	\N
LT	LITHUANIA	\N
LU	LUXEMBOURG	\N
MO	MACAU	\N
MK	MACEDONIA, THE FORMER YUGOSLAV	\N
MG	MADAGASCAR	\N
MW	MALAWI	\N
MY	MALAYSIA	\N
MV	MALDIVES	\N
ML	MALI	\N
MT	MALTA	\N
MH	MARSHALL ISLANDS	\N
MQ	MARTINIQUE	\N
MR	MAURITANIA	\N
MU	MAURITIUS	\N
YT	MAYOTTE	\N
MX	MEXICO	\N
FM	MICRONESIA, FEDERATED STATES O	\N
MD	MOLDOVA, REPUBLIC OF	\N
MC	MONACO	\N
MN	MONGOLIA	\N
MS	MONTSERRAT	\N
MA	MOROCCO	\N
MZ	MOZAMBIQUE	\N
MM	MYANMAR	\N
NA	NAMIBIA	\N
NR	NAURU	\N
NP	NEPAL	\N
NL	NETHERLANDS	\N
AN	NETHERLANDS ANTILLES	\N
NC	NEW CALEDONIA	\N
NZ	NEW ZEALAND	\N
NI	NICARAGUA	\N
NE	NIGER	\N
NG	NIGERIA	\N
NU	NIUE	\N
NF	NORFOLK ISLAND	\N
MP	NORTHERN MARIANA ISLANDS	\N
NO	NORWAY	\N
OM	OMAN	\N
PK	PAKISTAN	\N
PW	PALAU	\N
PS	PALESTINIAN TERRITORY, OCCUPIE	\N
PA	PANAMA	\N
PG	PAPUA NEW GUINEA	\N
PY	PARAGUAY	\N
PE	PERU	\N
PH	PHILIPPINES	\N
PN	PITCAIRN	\N
PL	POLAND	\N
PT	PORTUGAL	\N
PR	PUERTO RICO	\N
QA	QATAR	\N
RE	REUNION	\N
RO	ROMANIA	\N
RU	RUSSIAN FEDERATION	\N
RW	RWANDA	\N
SH	SAINT HELENA	\N
KN	SAINT KITTS AND NEVIS	\N
LC	SAINT LUCIA	\N
PM	SAINT PIERRE AND MIQUELON	\N
VC	SAINT VINCENT AND THE GRENADIN	\N
WS	SAMOA	\N
SM	SAN MARINO	\N
ST	SAO TOME AND PRINCIPE	\N
SA	SAUDI ARABIA	\N
SN	SENEGAL	\N
SC	SEYCHELLES	\N
SL	SIERRA LEONE	\N
SG	SINGAPORE	\N
SK	SLOVAKIA	\N
SI	SLOVENIA	\N
SB	SOLOMON ISLANDS	\N
SO	SOMALIA	\N
ZA	SOUTH AFRICA	\N
GS	SOUTH GEORGIA AND THE SOUTH SA	\N
ES	SPAIN	\N
LK	SRI LANKA	\N
SD	SUDAN	\N
SR	SURINAME	\N
SJ	SVALBARD AND JAN MAYEN	\N
SZ	SWAZILAND	\N
SE	SWEDEN	\N
CH	SWITZERLAND	\N
SY	SYRIAN ARAB REPUBLIC	\N
TW	TAIWAN, PROVINCE OF CHINA	\N
TJ	TAJIKISTAN	\N
TZ	TANZANIA, UNITED REPUBLIC OF	\N
TH	THAILAND	\N
TG	TOGO	\N
TK	TOKELAU	\N
TO	TONGA	\N
TT	TRINIDAD AND TOBAGO	\N
TN	TUNISIA	\N
TR	TURKEY	\N
TM	TURKMENISTAN	\N
TC	TURKS AND CAICOS ISLANDS	\N
TV	TUVALU	\N
UG	UGANDA	\N
UA	UKRAINE	\N
AE	UNITED ARAB EMIRATES	\N
GB	UNITED KINGDOM	\N
US	UNITED STATES	\N
\.




















































































































