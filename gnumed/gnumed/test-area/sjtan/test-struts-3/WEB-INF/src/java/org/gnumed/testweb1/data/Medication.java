/*
 * CurrentMedication.java
 *
 * Created on July 12, 2004, 6:57 AM
 */

package org.gnumed.testweb1.data;

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
     
}
