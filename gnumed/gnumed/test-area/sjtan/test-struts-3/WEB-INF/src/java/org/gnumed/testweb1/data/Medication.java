/*
 * CurrentMedication.java
 *
 * Created on July 12, 2004, 6:57 AM
 */

package org.gnumed.testweb1.data;

import java.util.Date;

/**
 *
 * @author  sjtan
 */
public interface  Medication extends ClinRootItem {
     public String getGenericName();
     public void setGenericName(String n);
     
     public String getBrandName();
     public void setBrandName(String b);
     
     public String getShortDescription();
     public void setShortDescription(String s);
     
     public java.util.Date getStart();
     public void setStart(java.util.Date  s);
     
     public java.util.Date getLast();
     public void setLast(java.util.Date l );
     
     public String getATC_code();
     public void setATC_code(String code);
     
     public String getDB_origin();
     public void setDB_origin(String origin);
     
     public String getDB_drug_id();
     public void setDB_drug_id(String id);
     
     public String getDirections();
     public void setDirections(String directions);
     
     public boolean isSR();
     public void setSR(boolean slowRelease);
     
     public boolean isPRN();
     public void setPRN(boolean PRN);
     
     public double getDose();
     public void setDose(double dose);
     
     public int getPeriod();
     public void setPeriod(int period);
     
     public Date getDiscontinued();
     public void setDiscontinued(Date d);

     public String getForm();
     public void setForm(String form);
     
     public String getAmountUnit();
     public void setAmountUnit(String unit);
    
     public int getQty();
     public void setQty(int qty);
     
     public int getRepeats();
     public void setRepeats(int repeats);
     
     public boolean isSubsidized();
     public void setSubsidized(boolean subsidized);
     
     public String getSubsidyScheme();
     public void setSubsidyScheme(String scheme);
     
     public int getMaxSubsidyRepeats();
     public void setMaxSubsidyRepeats(int repeats);
     
     public void setPresentation( String presentation);
     public String getPresentation();
     
     
     public String getConvertedAmountUnit();
     public void setConvertedAmountUnit(String convertedUnit);
     
     public double getConvertedDose();
     public void setConvertedDose(double dose);
     public void setConversionFactor(double factor);
     public double getConversionFactor();
     public void setPeriodString(String periodString);
     public String getPeriodString();
}
     
