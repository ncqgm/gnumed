--
-- Selected TOC Entries:
--
\connect - syan
--
-- TOC Entry ID 2 (OID 39041)
--
-- Name: person_view2 Type: VIEW Owner: syan
--
drop view person_view2;
CREATE VIEW "person_view2" as SELECT n.firstnames, n.lastnames, to_char(i.dob, 'DD-MM-YYYY') as dob , i.gender, i.id, a.street, a.addendum, p.phone1, p.phone2, i.pupic FROM identity i, "names" n, address a, identities_addresses ia, phone p WHERE ((((i.id = ia.id_identity) AND (a.id = ia.id_address)) AND (n.id_identity = i.id)) AND (p.id_identity = i.id));


