-- drop blob tables from GNUmed

-- license: GPL
-- author: Karsten Hilbert <Karsten.Hilbert@gmx.net>

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/Archive/server/Attic/dropBlobs.sql,v $
-- $Revision: 1.1 $ $Date: 2003-03-01 15:08:50 $ $Author: ncq $

drop table
	doc_type,
	doc_med,
	doc_med_external_ref,
	doc_obj,
	doc_desc
;

drop sequence
	doc_type_id_seq,
	doc_med_id_seq,
	dob_obj_id_seq,
	doc_desc_id_seq
;
