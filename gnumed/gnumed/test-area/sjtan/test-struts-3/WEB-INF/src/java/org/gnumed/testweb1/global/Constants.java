/*
 * Constants.java
 *
 * Created on June 18, 2004, 4:46 AM
 */

package org.gnumed.testweb1.global;

/**
 *
 * @author  sjtan
 */
public final class Constants {
    
    /** Creates a new instance of Constants */
    public Constants() {
    }
    
    public final static String LOGIN_MODULE= "LoginModule";
    public final static String JNDI_ROOT="java:/comp/env";
    public final static String JNDI_REF_POOLED_GNUMED_CONNECTIONS="/jdbc/gnumed";
    public final static String JNDI_REF_DRUGREF_CONNECTION="/jdbc/drugref";
    public final static String POOLED_DATASOURCE_GNUMED="dataSourceGnumed";
    public final static String POOLED_DATASOURCE_DRUGREF="dataSourceDrugRef";
   
    public static final int HOME_ADDRESS_TYPE = 1;
    
    public static final class Plugin {
        public final static String DEMOGRAPHIC_SQL_PROVIDER = "demographicSQLProvider";
        public final static String CLINICAL_SQL_PROVIDER = "clinicalSQLProvider";
        public final static String HEALTH_RECORD_ACCESS_PROVIDER = "healthRecordAccessProvider";
        public final static String DRUG_REF_ACCESS_PROVIDER = "drugRefAccessProvider";
    
    }
    
    public static final class Servlet {
        public final static String DEMOGRAPHIC_ACCESS= "demographicAccess";
         public final static String CLINICAL_ACCESS= "clinicalAccess";
          public final static String HEALTH_RECORD_ACCESS= "healthRecordAccess";
         public final static String OBJECT_FACTORY="objectFactory";
    
         public final static String DRUGREF_ACCESS= "drugRefAccess";
    }
    
    public static final  class Session {
        public final static String VACCINES= "vaccines";
        public final static String DEMOGRAPHIC_DETAILS="demographicDetails";
      
        public static final String HEALTH_RECORD = "healthRecord";
        
        public static final String DEMOGRAPHIC_DETAIL_CURRENT = "detail";
        
        public static final String TARGET_MEDICATION_ENTRY_INDEX="medEntryIndex";
        
        public static final String CURRENT_CLINICAL_FORM="currentClinicalForm";
    }
    
     public static final  class Request {
        public final static String PATIENT_ID="id";
        public final static String CLINICAL_UPDATE_FORM="clinicalUpdateForm";
    //    public final static String HEALTH_RECORD_DISPLAY="healthRecord";
        public final static String DRUG_NAME_PREFIX="drugNamePrefix";
        public final static String DRUG_REF_CANDIDATES="drugRefCandidates";
        public final static String MEDICATION_ENTRY_INDEX="medEntryIndex";
     }
     
     public static final class Schema {
         public final static String DEFAULT_HEALTH_ISSUE_LABEL="xxxDEFAULTxxx";
         public final static String DEFAULT_VACCINATION_HEALTH_ISSUE_RESOURCE_KEY="vaccination.default.health.issue";
         public final static String DEFAULT_VACCINATION_EPISODE_RESOURCE_KEY="vaccination.default.episode.description";
         public final static String DEFAULT_VACCINATION_NARRATIVE_RESOURCE_KEY="vaccination.default.narrative";
         public final static String DEFAULT_EPISODE_DESCRIPTION_KEY="default.episode.description";
     }
    
}
