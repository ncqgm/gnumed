drop view phx_view;
create view phx_view as SELECT  to_char(p.started, 'DD-MON-YYYY') AS date, '' AS fin, p.description, p.place,  p.extra, p.patient AS patient_id, p.clin_id FROM phx_event p  UNION SELECT to_char( phx_durable.started, 'DD-MON-YYYY') AS date, to_char(phx_durable.fin,  'DD-MON-YYYY') AS fin, phx_durable.description, phx_durable.place, phx_durable.extra,  phx_durable.patient AS patient_id, phx_durable.clin_id FROM phx_durable ;


