/*
 * ClinWhenEntryAdapter.java
 *
 * Created on September 25, 2004, 10:43 PM
 */

package org.gnumed.testweb1.data;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
/**
 *
 * @author  sjtan
 */
public class ClinWhenEntryAdapter   {
     DateEntryAdapter adapter; 
    static  Log log = LogFactory.getLog(ClinWhenEntryAdapter.class);
    
    /** Creates a new instance of ClinWhenEntryAdapter */
    public ClinWhenEntryAdapter(ClinWhenHolder target) {
        
        adapter  = new DateEntryAdapter(target, "clin_when");
    }
    
     
    public String getClinWhenString() {
        return adapter.getDateString();
    }
    
    public void setClinWhenString(String clinWhenString)  {
        try {
              adapter.setDateString(clinWhenString);
        } catch (Exception e) {
            log.error(e);
            throw new RuntimeException(e);
        }
    }
    
}
