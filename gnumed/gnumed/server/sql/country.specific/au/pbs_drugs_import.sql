-- ===============================================
-- This script imports drug data and ATC codes from
-- information as provided by the Australian authorities
-- (HIC) in the form of the PBS data updates
-- into Postgres tables
--
-- author: Dr. Horst Herb
-- version: 0.1
-- changelog:
--	21.10.2001: first implementation
--	30.11.2001: \set & \unset applied correctly
-- TODO: further processing of the data (normalizing)
-- ===============================================

-- force terminate + exit(3) on errors if non-interactive
\set ON_ERROR_STOP 1

-- =============================================

\unset ON_ERROR_STOP
drop table pbsimport;
\set ON_ERROR_STOP 1
create table pbsimport (
	drugtypecode char(2),
	atccode char(7),
	atctype char,
	atcprintopt char,
	pbscode char(4),
	restrictionflag char,
	cautionflag char,
	noteflag char,
	maxquantity int,
	numrepeats int,
	manufacturercode char(2),
	packsize int,
	brandpricepremium money,
	thergrouppremium money,
	cwprice money,
	cwdprice money,
	thergroupprice money,
	thergroupdprice money,
	manufactprice money,
	manufactdprice money,
	maxvalsafetynet money,
	bioequivalence char,
	brandname text,
	genericname text,
	formandstrength text
);

-- ===============================================
-- fill the table with the current data
-- ===============================================
\copy pbsimport from 'Drug.txt' using delimiters '!'

-- ===============================================
-- do the same thing with the ATC codes
-- ===============================================
\unset ON_ERROR_STOP
drop table atc;
\set ON_ERROR_STOP 1

create table atc (
	code char(7) primary key,
	text text
);
-- ===============================================
-- fill the table with the current data
-- ===============================================
\copy atc from 'Atc.txt' using delimiters '!'

-- ===============================================
-- do the same thing with the manufacturer details
-- ===============================================
\unset ON_ERROR_STOP
drop table manufacturer;
\set ON_ERROR_STOP 1
create table manufacturer (
	code char(2) primary key,
	name text,
	adress text,
	telephone text,
	facsimile text
);
-- ===============================================
-- fill the table with the current data
-- ===============================================
\copy manufacturer from 'Mnfr.txt' using delimiters '!'

-- ===============================================
-- try it out
-- ===============================================
select distinct p.genericname, a.text, m.name
from pbsimport p, atc a, manufacturer m
where p.atccode=a.code and p.manufacturercode = m.code limit 20;
