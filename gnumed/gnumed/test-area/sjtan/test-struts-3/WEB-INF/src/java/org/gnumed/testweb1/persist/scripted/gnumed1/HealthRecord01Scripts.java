/*
 * HealthRecord01Scripts.java
 *
 * Created on September 14, 2004, 11:01 PM
 */

package org.gnumed.testweb1.persist.scripted.gnumed1;

/**
 *
 * @author  sjtan
 */
public class HealthRecord01Scripts {
    public final static String[] newHealthIssue =  {
        "insert into clin_health_issue( id_patient, description) values ( {0} , '{1}')"
    };
    public final static String[] newClinEpisode = {
        "insert into clin_episode( fk_health_issue, description) values ( {0}, '{1}')"
    };
    
    public final static String[] newClinEncounter = {
        "insert into clin_encounter( fk_patient, fk_type, description, started ) " +
        " values( {0 ,number,long}, {1}, '{2}', {3} )"    
    };
    
    public final static String[] newNarrative =  {
        "insert into clin_narrative( clin_when, fk_encounter, fk_episode, narrative, soap_cat) " +
        " values ( {0}, {1}, {2}, '{3}', '{4}' )" ,
        "insert into clin_diag ( fk_narrative, laterality, is_chronic, is_active, is_definite, is_signifcant" +
        " values ( {0}, '{1}', {2}, {3}, {4} "
       
    };
    
    public final static String[] newCurrentMedication = {
        "insert into current_medication ( fk_encounter, fk_episode, narrative, soap_cat"+
        ", started, last_prescribed, expires, brandname, adjuvant, db_origin, db_xref "+
        "atc_code, amount_unit, dose, period, form ,directions, prn , sr ) " +
        "values ( {0}, {1} , '{2}', 'p', " +
        " {3}, {4}, {5}, '{6}', '{7}', '{8}', '{9}' , " +
        " '{10}', '{11}', {12, double}, {13, integer}, '{14}', '{15}',  {16}, {17} )"
        
    };
    
     public final static String[] newAllergy = {
         "insert into allergy (fk_encounter, fk_episode,id_type,  narrative," +
         " substance, generics, generic_specific, definite ) values (" +
         "{0}, {1}, {2}, '{3}', '{4}', '{5}', {6}, {7} ) "
     };
    
  
    
    
    /** Creates a new instance of HealthRecord01Scripts */
    public HealthRecord01Scripts() {
    }
    
}
