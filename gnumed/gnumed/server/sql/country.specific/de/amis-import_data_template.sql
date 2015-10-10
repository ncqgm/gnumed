-- ===============================================
-- This script imports drug data and ATC codes from
-- information provided by the german AMIS database
-- into Postgres tables

-- author: Horst Herb, Hilmar Berger, Karsten Hilbert
-- license: GPL v2 or later

-- =====================================================================================
-- amis_praeparate : table of preparations
\copy amis_praeparate from 'AMIS_PATH/basis/praepara.ami' using delimiters '$' WITH NULL AS '' 

-- amis_praeparate : table of preparations (combinations of more than one drug /package)
\copy amis_praeparate_combination from 'AMIS_PATH/basis/praepara.kpg' using delimiters '$' WITH NULL AS ''

-- amis_substances : table of substances
\copy amis_substances from 'AMIS_PATH/basis/stoffe.ami' using delimiters '$' WITH NULL AS ''

-- amis_substances_extended : extended info of substances
\copy amis_substances_extended from 'AMIS_PATH/basis/stof_erw.ami' using delimiters '$' WITH NULL AS ''

-- amis_substances_names : names of substances
\copy amis_substances_names from 'AMIS_PATH/basis/stoffbez.ami' using delimiters '$' WITH NULL AS ''

-- amis_indications 
\copy amis_indications from 'AMIS_PATH/basis/indikati.ami' using delimiters '$' WITH NULL AS ''

-- amis_warnings 
\copy amis_warnings from 'AMIS_PATH/basis/wh_verkn.ami' using delimiters '$' WITH NULL AS ''

-- amis_warning_text 
\copy amis_warning_text from 'AMIS_PATH/basis/warnhinw.ami' using delimiters '$' WITH NULL AS ''

-- amis_manufacturer
\copy amis_manufacturer from 'AMIS_PATH/basis/herstell.ami' using delimiters '$' WITH NULL AS ''

-- amis_manuf_emergency_call
\copy amis_manuf_emergency_call from 'AMIS_PATH/basis/notrufnu.ami' using delimiters '$' WITH NULL AS ''

-- do the same thing with the ATC codes
\copy amis_atc from 'AMIS_PATH/basis/atc_text.ami' using delimiters '$' WITH NULL AS ''

-- amis drug descriptions
\copy amis_drug_description from 'AMIS_PATH/basis/texte_pr.ami' using delimiters '$' WITH NULL AS ''

-- amis substance descriptions
\copy amis_substance_description from 'AMIS_PATH/basis/texte_st.ami' using delimiters '$' WITH NULL AS ''

-- amis prices
\copy amis_price from 'AMIS_PATH/basis/taxe.ami' using delimiters '$' WITH NULL AS ''

-- amis_price_manufacturer
\copy amis_price_manufacturer from 'AMIS_PATH/basis/neu/taxe_her.ami' using delimiters '$' WITH NULL AS ''

-- amis_presentation
\copy amis_presentation from 'AMIS_PATH/basis/darreich.ami' using delimiters '$' WITH NULL AS ''

-- amis_interaction_groups
\copy amis_interaction_groups from 'AMIS_PATH/interakt/interakt.int' using delimiters '$' WITH NULL AS ''

-- amis_documented_interaction
\copy amis_documented_interaction from 'AMIS_PATH/interakt/erwiesen.int' using delimiters '$' WITH NULL AS ''

-- amis_expected_interaction
\copy amis_expected_interaction from 'AMIS_PATH/interakt/erwartet.int' using delimiters '$' WITH NULL AS ''

-- amis_undecided_interaction
\copy amis_undecided_interaction from 'AMIS_PATH/interakt/keine_au.int' using delimiters '$' WITH NULL AS ''

-- amis_unlikely_interaction
\copy amis_unlikely_interaction from 'AMIS_PATH/interakt/ausgesch.int' using delimiters '$' WITH NULL AS ''

-- amis_interaction_type
\copy amis_interaction_type from 'AMIS_PATH/interakt/typ_inte.int' using delimiters '$' WITH NULL AS ''

-- amis_interaction_text
\copy amis_interaction_text from 'AMIS_PATH/interakt/texte.int' using delimiters '$' WITH NULL AS ''

-- ===============================================
-- try it out
-- ===============================================

CREATE INDEX idx__praeparate_conn_id ON amis_praeparate (connection_id);
CREATE INDEX idx__praeparate_brandname ON amis_praeparate (brandname);

CREATE INDEX idx_substance_id ON amis_substances (id);
CREATE INDEX idx_substance_name ON amis_substances_names (substance_name);

CREATE INDEX idx_drug_desc_text_key on amis_drug_description (text_key);

-- ===============================================
