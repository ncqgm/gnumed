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
    public final static String JNDI_REF_POOLED_CONNECTIONS="/jdbc/gnumed";
    public final static String POOLED_DATASOURCE="dataSource";
    
   
    public static final int HOME_ADDRESS_TYPE = 1;
    
    public static final class Plugin {
        public final static String DEMOGRAPHIC_SQL_PROVIDER = "demographicSQLProvider";
        public final static String CLINICAL_SQL_PROVIDER = "clinicalSQLProvider";
        public final static String HEALTH_RECORD_ACCESS_PROVIDER = "healthRecordAccessProvider";
   
    
    }
    
    public static final class Servlet {
        public final static String DEMOGRAPHIC_ACCESS= "demographicAccess";
         public final static String CLINICAL_ACCESS= "clinicalAccess";
          public final static String HEALTH_RECORD_ACCESS= "healthRecordAccess";
         public final static String OBJECT_FACTORY="objectFactory";
    
    }
    
    public static final  class Session {
        public final static String VACCINES= "vaccines";
        public final static String DEMOGRAPHIC_DETAILS="demographicDetails";
      
    }
    
     public static final  class Request {
        public final static String PATIENT_ID="id";
        public final static String DEMOGRAPHIC_DETAIL_DISPLAY = "detail";
        public final static String CLINICAL_UPDATE_FORM="clinicalUpdateForm";
        public final static String HEALTH_RECORD_DISPLAY="healthRecord";
        
     }
    
}
