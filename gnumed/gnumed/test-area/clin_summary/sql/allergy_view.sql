drop view allergy_view;
 create view allergy_view as select  to_char(started, 'DD-MON-YYYY') as date, drug, description, patient as patient_id, clin_id from allergy;  

