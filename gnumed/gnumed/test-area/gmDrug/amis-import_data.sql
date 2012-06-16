-- ===============================================
-- This script imports drug data and ATC codes from
-- information provided by the german AMIS database
-- into Postgres tables

-- $Source: /home/ncq/Projekte/cvs2git/vcs-mirror/gnumed/gnumed/test-area/gmDrug/amis-import_data.sql,v $
-- author: Horst Herb, Hilmar Berger, Karsten Hilbert
-- version: $Revision: 1.5 $
-- license: GPL v2 or later

-- =====================================================================================
-- amis_praeparate : table of preparations
\copy amis_praeparate from './amis-orig/basis/praepara.ami' using delimiters '$'

-- amis_praeparate : table of preparations (combinations of more than one drug /package)
\copy amis_praeparate_combination from './amis-orig/basis/praepara.kpg' using delimiters '$'

-- amis_substances : table of substances
\copy amis_substances from './amis-orig/basis/stoffe.ami' using delimiters '$'

-- amis_substances_extended : extended info of substances
\copy amis_substances_extended from './amis-orig/basis/stof_erw.ami' using delimiters '$'

-- amis_substances_names : names of substances
\copy amis_substances_names from './amis-orig/basis/stoffbez.ami' using delimiters '$'

-- amis_indications 
\copy amis_indications from './amis-orig/basis/indikati.ami' using delimiters '$'

-- amis_warnings 
\copy amis_warnings from './amis-orig/basis/wh_verkn.ami' using delimiters '$'

-- amis_warning_text 
\copy amis_warning_text from './amis-orig/basis/warnhinw.ami' using delimiters '$'

-- amis_manufacturer
\copy amis_manufacturer from './amis-orig/basis/herstell.ami' using delimiters '$'

-- amis_manuf_emergency_call
\copy amis_manuf_emergency_call from './amis-orig/basis/notrufnu.ami' using delimiters '$'

-- do the same thing with the ATC codes
\copy amis_atc from './amis-orig/basis/atc_text.ami' using delimiters '$'

-- amis drug descriptions
\copy amis_drug_description from './amis-orig/basis/texte_pr.ami' using delimiters '$'

-- amis substance descriptions
\copy amis_substance_description from './amis-orig/basis/texte_st.ami' using delimiters '$'

-- amis prices
\copy amis_price from './amis-orig/basis/taxe.ami' using delimiters '$'

-- amis_price_manufacturer
\copy amis_price_manufacturer from './amis-orig/basis/neu/taxe_her.ami' using delimiters '$'

-- amis_presentation
\copy amis_presentation from './amis-orig/basis/darreich.ami' using delimiters '$'

-- amis_interaction_groups
\copy amis_interaction_groups from './amis-orig/interakt/interakt.int' using delimiters '$'

-- amis_documented_interaction
\copy amis_documented_interaction from './amis-orig/interakt/erwiesen.int' using delimiters '$'

-- amis_expected_interaction
\copy amis_expected_interaction from './amis-orig/interakt/erwartet.int' using delimiters '$'

-- amis_undecided_interaction
\copy amis_undecided_interaction from './amis-orig/interakt/keine_au.int' using delimiters '$'

-- amis_unlikely_interaction
\copy amis_unlikely_interaction from './amis-orig/interakt/ausgesch.int' using delimiters '$'

-- amis_interaction_type
\copy amis_interaction_type from './amis-orig/interakt/typ_inte.int' using delimiters '$'

-- amis_interaction_text
\copy amis_interaction_text from './amis-orig/interakt/texte.int' using delimiters '$'

-- ===============================================
-- try it out
-- ===============================================

CREATE INDEX idx__praeparate_conn_id ON amis_praeparate (connection_id);
CREATE INDEX idx__praeparate_brandname ON amis_praeparate (brandname);

CREATE INDEX idx_substance_id ON amis_substances (id);
CREATE INDEX idx_substance_name ON amis_substances_names (substance_name);

CREATE INDEX idx_drug_desc_text_key on amis_drug_description (text_key);

-- ===============================================
-- $Log: amis-import_data.sql,v $
-- Revision 1.5  2002-11-11 08:22:42  ncq
-- - amis_orig -> amis-orig
--
-- Revision 1.4  2002/11/10 22:31:11  hinnef
-- removed some useless lines
--
-- Revision 1.3  2002/11/10 16:15:06  ncq
-- - added index
--
-- Revision 1.2  2002/11/10 14:13:25  ncq
-- - source dir for taxe_her.ami was wrong
--
-- Revision 1.1  2002/10/24 12:56:38  ncq
-- - initial checkin
-- - split into creation of tables and import of data so people
--   without the data can still import the structure
-- - fix whitespace and typos, make layout more consistent
--
