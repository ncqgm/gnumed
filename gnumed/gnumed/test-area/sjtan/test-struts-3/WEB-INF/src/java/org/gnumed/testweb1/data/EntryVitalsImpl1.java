/*
 * EntryVitalsImpl1.java
 *
 * Created on 26 October 2004, 07:46
 */

package  org.gnumed.testweb1.data;
import java.util.HashSet;
import java.util.Set;

import org.apache.commons.beanutils.PropertyUtils;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.gnumed.testweb1.global.Util;
/**
 *
 * @author  sjtan
 * checks to see if there is a significant change in values.
 *
 */
public class EntryVitalsImpl1 extends VitalsImpl1 implements EntryVitals {
    Log log = LogFactory.getLog(EntryVitalsImpl1.class);
    public   class ChangeChecker {
        Vitals v;
        Set set = new HashSet();
        
        public ChangeChecker(Vitals v) {
            this.v  = v;
        }
        
        void add(String property, double val) {
            try {
                Object o = PropertyUtils.getProperty( v, property);
                Number n = (Number)o;
                
                double oldVal = n.doubleValue();
                if (java.lang.Math.abs(val-oldVal) >(double) 0.001 ) {
                    log.info("**** THE PROPERTY "+ property + " changed.");
                    set.add(property);
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
        
        void add(String property , int value) {
            add(property, (double) value);
        }
        
        void add(String property, String value) {
            try {
                Object o = PropertyUtils.getProperty( v, property);
                String s = (String)o;
                value = Util.nullIsBlank(value);
                if(!"".equals(value) && !value.equals(s)) {
                    set.add(property);
                }
                
            } catch (Exception e) {
                e.printStackTrace();
            }
            
        }
        
        public boolean contains(String prop) {
            return set.contains(prop);
        }
        
        public boolean isChanged() {
            return set.size() != 0;
            
        }
    }
    
    private ChangeChecker set = new ChangeChecker(this);
    
    boolean  linked;
    /** Creates a new instance of EntryVitalsImpl1 */
    ClinWhenEntryAdapter adapter = new ClinWhenEntryAdapter(this);
    
    public EntryVitalsImpl1() {
        
        linked = false;
    }
    
    public String getClinWhenString() {
        return adapter.getClinWhenString();
        
    }
    
   
    
    public boolean isLinkedToPreviousEpisode() {
        return linked;
    }
    
    public void setClinWhenString(String clinWhenString) {
        adapter.setClinWhenString(clinWhenString);
    }
    
    public void setEntered(boolean entered) {
        
    }
    
    public void setLinkedToPreviousEpisode(boolean linkedToPreviousEpisode) {
        linked = linkedToPreviousEpisode;
    }
    
    public boolean isSet(String propertyName) {
        return set.contains(propertyName);
    }
    /**
     * Setter for property systolic.
     * @param systolic New value of property systolic.
     */
    public void setSystolic(int systolic) {
        set.add("systolic", systolic );
        super.setSystolic(systolic);
    }
    
    
    /**
     * Setter for property diastolic.
     * @param diastolic New value of property diastolic.
     */
    public void setDiastolic(int diastolic) {
        set.add("diastolic", diastolic);
        super.setDiastolic(diastolic);
    }
    
    
    
    /**
     * Setter for property rr.
     * @param rr New value of property rr.
     */
    public void setRr(int rr) {
        set.add("rr",rr);
        super.setRr(rr);
    }
    
    
    /**
     * Setter for property pr.
     * @param pr New value of property pr.
     */
    public void setPr(int pr) {
        set.add("pr",pr);
        super.setPr(pr);
    }
    
    
    /**
     * Setter for property temp.
     * @param temp New value of property temp.
     */
    public void setTemp(double temp) {
        set.add("temp", temp);
        super.setTemp(temp);
    }
    
    
    /**
     * Setter for property weight.
     * @param weight New value of property weight.
     */
    public void setWeight(double weight) {
        set.add("weight", weight );
        super.setWeight(weight);
        
    }
    
    
    
    /**
     * Setter for property height.
     * @param height New value of property height.
     */
    public void setHeight(double height) {
        set.add("height", height);
        super.setHeight(height);
        
    }
    
    
    /**
     * Setter for property pefr.
     * @param pefr New value of property pefr.
     */
    public void setPrepefr(int pefr) {
        set.add("prepefr",  pefr);
        super.setPrepefr(pefr);
    }
    
    
    
    /**
     * Setter for property rhythm.
     * @param rhytm New value of property rhythm.
     */
    public void setRhythm(String rhythm) {
        set.add("rhythm", rhythm);
        super.setRhythm(rhythm);
    }
    
    
    /**
     * Setter for property postpefr.
     * @param postpefr New value of property postpefr.
     */
    public void setPostpefr(int postpefr) {
        set.add("postpefr", postpefr);
        super.setPostpefr(postpefr);
    }
 
    
    public boolean isEntered() {
        return set.isChanged();
    
    }
    
    public String getHeightString() {
        return Double.toString(getHeight());
    }
    
    public void setHeightString(String heightString) {
        try {
        setHeight(Double.parseDouble(heightString.trim()));
        } catch (NumberFormatException e) {
            log.info("Error :" + e, e);
        }
    }
    
    public String getWeightString() {
        return Double.toString(getWeight());
    }
    
    public void setWeightString(String weightString) {
         try {
          log.info("TRYING TO SET WEIGHT w/"+ weightString);
          setWeight(Double.parseDouble(weightString.trim()));
          log.info("succeeded in setting to " + getWeight());
          } catch (NumberFormatException e) {
            log.info("Error :" + e, e);
        }
    }
    
}
