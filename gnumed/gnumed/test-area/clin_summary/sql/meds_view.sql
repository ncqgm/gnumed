--
-- Selected TOC Entries:
--
\connect - syan
--
-- TOC Entry ID 2 (OID 39001)
--
-- Name: meds_view Type: VIEW Owner: syan
--

CREATE VIEW "meds_view" as SELECT  m.clin_id, dp.name AS drug, md.dose, du.description AS unit, dr.description AS route, mt.descript AS freq, mq.qty, mq.repeats, md.started, md.fin AS ceased , m.patient as patient_id FROM meds m, drug_presentation dp, med_dose md, amount_unit du, drug_route dr, med_timing mt, med_qty mq WHERE ((((((m.drug_info = dp.id) AND (m.clin_id = md.meds_id)) AND (m.clin_id = mq.meds_id)) AND (dp.route = dr.id)) AND (dp.amount_unit = du.id)) AND (md.timing = mt.clin_id));

