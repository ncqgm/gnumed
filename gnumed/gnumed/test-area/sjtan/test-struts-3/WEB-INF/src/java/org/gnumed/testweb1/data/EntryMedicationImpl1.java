/*
 * Created on 09-Oct-2004
 *
 */
package org.gnumed.testweb1.data;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;

//import org.gnumed.testweb1.business.ConversionRules;
import org.gnumed.testweb1.global.Constants;
import org.gnumed.testweb1.global.Util;
import org.apache.commons.logging.*;
/**
 * @author sjtan
 *
 *
 */
public class EntryMedicationImpl1 extends MedicationImpl1 implements
EntryMedication , Medication{
    static Log log = LogFactory.getLog(EntryMedicationImpl1.class);
    private int index;
    private HashMap conversionRules = new HashMap();
    
    EntryClinRootItem item = new EntryClinRootItemImpl1();
    
        /* (non-Javadoc)
         * @see org.gnumed.testweb1.data.ClinWhenEntryHolder#getClinWhenString()
         */
    public String getClinWhenString() {
        return item.getClinWhenString();
    }
    
        /* (non-Javadoc)
         * @see org.gnumed.testweb1.data.ClinWhenEntryHolder#setClinWhenString(java.lang.String)
         */
    public void setClinWhenString(String clinWhenString) {
        item.setClinWhenString(clinWhenString);
        
    }
    
        /* (non-Javadoc)
         * @see org.gnumed.testweb1.data.EntryClinRootItem#isEntered()
         */
    public boolean isEntered() {
        if (log.isInfoEnabled()) {
            log.info("For drug "+ getBrandName() + " hasDrugName()=" + hasDrugName() + "; qty="+getQty() +  "rpts=" +getRepeats());
        }
        return hasDrugName() && getQty() > 0 && getRepeats() >= 0 ;
    }
    
    /**
     * @return
     */
    private boolean hasDrugName() {
        return !"".equals(Util.nullIsBlank(getBrandName()) )
        || ! "".equals(Util.nullIsBlank(getGenericName()));
    }
    
        /* (non-Javadoc)
         * @see org.gnumed.testweb1.data.EntryClinRootItem#setEntered(boolean)
         */
    public void setEntered(boolean entered) {
        item.setEntered(entered);
    }
    
        /* (non-Javadoc)
         * @see org.gnumed.testweb1.data.EntryClinRootItem#isLinkedToPreviousEpisode()
         */
    public boolean isLinkedToPreviousEpisode() {
        
        return item.isLinkedToPreviousEpisode();
    }
    
        /* (non-Javadoc)
         * @see org.gnumed.testweb1.data.EntryClinRootItem#setLinkedToPreviousEpisode(boolean)
         */
    public void setLinkedToPreviousEpisode(boolean linkedToPreviousEpisode) {
        item.setLinkedToPreviousEpisode(linkedToPreviousEpisode);
    }
    
    public int getIndex() {
        return index;
    }
    
    public void setIndex(int i) {
        this.index = i;
    }
    
    public java.util.Map getSearchParams() {
        HashMap map = new HashMap();
        map.put(Constants.Request.MEDICATION_ENTRY_INDEX, new Integer(getIndex()));
        map.put(Constants.Request.DRUG_NAME_PREFIX, getBrandName());
        return map;
    }
    
    public void setBrandName(String b) {
        super.setBrandName(b);
        if ( log.isInfoEnabled()) {
            log.info("Brandname for " + this + " was set to " + b);
        }
    }
    
    
    /** these rules need to match the constraints on clin_medication
     */
    
    public void setAmountUnit(String unit) {
        unit =  (unit ==null? "each" : unit.trim().toLowerCase() );
        setConversionFactor(1.0);
        if ("mg".equals(unit)) {
        	setConvertedAmountUnit("g");
        	setConversionFactor(0.001);
        }
        
        else if("mcg".equals(unit)) {
        	setConvertedAmountUnit("g");
        	setConversionFactor(0.000001);
        	
        } else if ("dose".equals(unit)) {
        	setConvertedAmountUnit("each");
        	
        } else if ("day".equals(unit)) {
        	setConvertedAmountUnit("each");
        	
        } else {
        	setConvertedAmountUnit(unit);
        }
        super.setAmountUnit(unit);
    }
	
    public void setConvertedAmountUnit(String unit) {
    	 unit =  (unit ==null? "each" : unit.trim().toLowerCase() );
         
         if ("g".equals(unit)) {
         	if ("mg".equals(getAmountUnit())) {
         		setConversionFactor(0.001);
         	}
         }
         if (getAmountUnit() == null || "".equals(getAmountUnit().trim())) {
         	super.setAmountUnit(unit);
         }
         super.setConvertedAmountUnit(unit);
    }
    
    public void setDose(double dose) {
    	super.setConvertedDose(getConversionFactor() * dose);
    	super.setDose(dose);
    }
    
   public void setConvertedDose(double dose) {
   		super.setDose( dose / getConversionFactor());
   		super.setConvertedDose(dose);
   }
  
   public void setPeriodString(String s) {
   		super.setPeriodString(s);
   		s = Util.nullIsBlank(s);
   		s =s.trim();
   		s= s.toLowerCase();
   		if ( "mane".equals(s) || "nocte".equals(s) || 
   				s.startsWith("a day") || "daily".equals(s) || "^once.*da.*".equals(s) || "od".equals(s)) {
   			setPeriod(Constants.Schema.Medication.ONCE_DAILY);
   		}
   		else if ( "bd".equals(s) || s.startsWith("twice da")
   					|| s.matches("^2 times.*da" )) {
   			setPeriod(Constants.Schema.Medication.TWICE_A_DAY);
   		}
   		else if (
   				"tds".equals(s) || s.matches("^3 times.*da.*") 
   				|| s.matches ( "^8\\s*h\\w*r.*" ) ) {
			   			setPeriod(Constants.Schema.Medication.THREE_DAILY);
			   			 
   		} else if ( "qid".equals(s) || s.matches("^6\\s*h\\w*r.*") ) {
   			setPeriod(Constants.Schema.Medication.FOUR_DAILY);
   			
   		} else if (s.matches("^six*h.*r.*" ) || s.matches("^six.*h.*r.*") ) {
   			setPeriod( Constants.Schema.Medication.FOUR_DAILY);
   			
   	    }else if (s.matches("^4.*h.*r.*" ) || s.matches("^four.*h.*r.*") ) {
   			setPeriod( Constants.Schema.Medication.SIX_DAILY);
   			
   		} else if ( s.matches("5 times.*da.*") ) {
   			setPeriod(Constants.Schema.Medication.FIVE_DAILY);
   			
   		}  else if (s.matches("alt.*da.*") || s.matches("2\\w*days")
   				|| s.matches("every.*2nd.*day") || s.matches("second.*da.*")) {
   			setPeriod(Constants.Schema.Medication.ALT_DAILY);
   			
   		} else if (s.matches("once.*week.*") || s.matches("once a week.*") ) {
   			setPeriod(Constants.Schema.Medication.ONCE_WEEKLY);
   			
   		} else if ( s.matches("twice.*week.*")  || (s).matches("2 times.*week.*")) {
   			 setPeriod(Constants.Schema.Medication.TWICE_WEEKLY) ;
   		   	
   		}
   		
   		
   		
   }
   
   /**
 *  updates the directions string with the parsed data .
 */
public void updateDirections() {
	String d = Util.nullIsBlank(getDirections());
	
	setDirections(String.valueOf(getDose()) +" " +
			getPresentation() + " " + getPeriodString() +  ( isPRN()? " prn": "" )+ "; " + String.valueOf(getQty()) + " x " +String.valueOf(getRepeats())+"rpt" + ("".equals(d) ?"":" ; ") + d);

}

public void setPeriod(int period) {
   		super.setPeriod(period);
   		if (  null== getPeriodString()||"".equals(getPeriodString().trim())  ) {
   				if (period == Constants.Schema.Medication.TWICE_WEEKLY) {
   					setPeriodString("twice weekly");
   				} 
   				else if ( period == Constants.Schema.Medication.ONCE_WEEKLY ) {
   					setPeriodString("once weekly");
   				}
   				else if (period == Constants.Schema.Medication.ALT_DAILY  ) {
   					setPeriodString("alternate daily") ;
   				} else if (period == Constants.Schema.Medication.ONCE_DAILY ) {
   					setPeriodString("24 hourly") ;
   				} else if (period == Constants.Schema.Medication.TWICE_A_DAY) {
   					setPeriodString("twice a day") ;
   				} else if (period == Constants.Schema.Medication.THREE_DAILY ) {
   					setPeriodString("three times a day");
   				}else if (period == Constants.Schema.Medication.FOUR_DAILY) {
   					setPeriodString("four times a day");
   				}else if (period == Constants.Schema.Medication.SIX_DAILY) {
   					setPeriodString("six  times a day");
   				}else if (period ==Constants.Schema.Medication.FIVE_DAILY) {
   					setPeriodString("5 times a day");
   				}
   		}
   }
   
   public void setForm(String form) {
       form = Util.nullIsBlank(form);
       form = form.toLowerCase();
       super.setForm(Constants.Schema.Medication.getGnumedFromDrugRefForm(form));
       log.info("** FORM WAS SET TO " + form );
   }
}
