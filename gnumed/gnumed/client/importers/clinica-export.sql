begin;

-- next patient
INSERT INTO dem.identity (gender, dob, comment) VALUES ('m', NULL, 'Clinica import @ 2012-01-18T16:00:06.284053+01:00');
UPDATE dem.identity SET dob = '1921 03 21 00 00 00'::timestamp with time zone WHERE pk = currval('dem.identity_pk_seq');
SELECT dem.add_name(currval('dem.identity_pk_seq'), 'Kirk', 'Tiberius', True);
INSERT INTO dem.lnk_identity2ext_id (id_identity, external_id, fk_origin) VALUES (currval('dem.identity_pk_seq'), '1', dem.add_external_id_type('Clinica primary key', 'Clinica EMR'));
INSERT INTO dem.lnk_identity2ext_id (id_identity, external_id, fk_origin) VALUES (currval('dem.identity_pk_seq'), 'code-fiscale', dem.add_external_id_type('Clinica-external ID', 'Clinica EMR'));
INSERT INTO dem.lnk_identity2phone (fk_identity, url, fk_type) VALUES (currval('dem.identity_pk_seq'), 'kirk-phone', dem.create_comm_type('homephone'));
INSERT INTO dem.lnk_identity2phone (fk_identity, url, fk_type) VALUES (currval('dem.identity_pk_seq'), 'Cunnersdorfer Str. 11', dem.create_comm_type('Clinica address'));
INSERT INTO clin.clin_narrative (soap_cat, clin_when, fk_encounter, fk_episode, narrative) VALUES ('s', '2012 01 16 11 28 34'::timestamp with time zone, E'Anamnese', currval('clin.encounter_pk_seq'), currval('clin.episode_pk_seq'));
INSERT INTO clin.clin_narrative (soap_cat, clin_when, fk_encounter, fk_episode, narrative) VALUES ('o', '2012 01 16 11 28 34'::timestamp with time zone, E'Physical exam\n\nLab work:\nlab exam\n\nHistopathology:\nhisto exam', currval('clin.encounter_pk_seq'), currval('clin.episode_pk_seq'));
INSERT INTO clin.clin_narrative (soap_cat, clin_when, fk_encounter, fk_episode, narrative) VALUES ('a', '2012 01 16 11 28 34'::timestamp with time zone, E'Diagnosis', currval('clin.encounter_pk_seq'), currval('clin.episode_pk_seq'));
INSERT INTO clin.clin_narrative (soap_cat, clin_when, fk_encounter, fk_episode, narrative) VALUES ('p', '2012 01 16 11 28 34'::timestamp with time zone, E'Topical therapy:\ntopical therapie\n\nSystemic therapy:\nsystemic therapy\n\nSubsequent checks:\nsubsequent checks', currval('clin.encounter_pk_seq'), currval('clin.episode_pk_seq'));

commit;
