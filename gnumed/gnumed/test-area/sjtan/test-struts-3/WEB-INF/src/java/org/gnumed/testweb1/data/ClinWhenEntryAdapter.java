/*
 * ClinWhenEntryAdapter.java
 *
 * Created on September 25, 2004, 10:43 PM
 */

package org.gnumed.testweb1.data;
import java.text.SimpleDateFormat;
import java.text.DateFormat;
import org.gnumed.testweb1.global.Util;
import java.util.*;
import org.apache.commons.logging.*;
/**
 *
 * @author  sjtan
 */
public class ClinWhenEntryAdapter  {
    ClinWhenHolder target;
    
    static  Log log = LogFactory.getLog(ClinWhenEntryAdapter.class);
    
    /** Creates a new instance of ClinWhenEntryAdapter */
    public ClinWhenEntryAdapter(ClinWhenHolder target) {
        this.target = target;
    }
    
     
    public String getClinWhenString() {
        return Util.getShortestDateTimeString(target.getClin_when());
    }
    
    public void setClinWhenString(String clinWhenString)  {
        try {
            log.info("Clin WHEN STRING PARSES TO " +Util.parseDate(clinWhenString.trim() ));
            target.setClin_when(Util.parseDate(clinWhenString.trim()));
        } catch (Exception e) {
            log.error(e);
            throw new RuntimeException(e);
        }
    }
    
}
