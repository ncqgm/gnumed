-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: Karsten Hilbert
--
-- ==============================================================
\set ON_ERROR_STOP 1

-- --------------------------------------------------------------
delete from cfg.report_query where label = 'Find invoices attached to the wrong patient';

insert into cfg.report_query (label, cmd) values (
	'Find invoices attached to the wrong patient',
'-- shows invoices which are not attached to the patient the corresponding bill is about,
-- this could happen due to a bug between 1.2.0 (17.0) and 1.2.4 (17.4)

-- such invoices need manual correction by:
-- 1) activating the "pk_invoice_patient"
-- 2) deleting the invoice from the pool of documents of the "pk_bill_patient"
-- 3) activating the "pk_bill_patient"
-- 4) re-creating the invoice by selecting the bill and attempting to show the PDF

SELECT
	pk_bill,
	invoice_id,
	b_vb.pk_patient AS pk_bill_patient,
	b_vdm.pk_patient AS pk_invoice_patient
FROM
	bill.v_bills b_vb INNER JOIN blobs.v_doc_med b_vdm ON (b_vb.pk_doc = b_vdm.pk_doc)
WHERE
	b_vb.pk_patient IS DISTINCT FROM b_vdm.pk_patient
;');

-- --------------------------------------------------------------
select gm.log_script_insertion('v17-cfg-report_query-fixup.sql', '17.4');
