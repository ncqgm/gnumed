/*
 * Created on 12-Oct-2004
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
package org.gnumed.testweb1.data;

/**
 * @author sjtan
 *
 * TODO To change the template for this generated type comment go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
public interface DrugRef {
	public String getBrandName();
	public String getATC_code();
	public String getATC();
	public String getDescription();
	public int getSubsidizedRepeats();
	public int getSubsidizedQuantity();
	public int getDefaultRepeats();
	public int getDefaultQuantity();
	public int getPackageSize();
	public Integer getId();
	public String getRouteAbbrev();
	public String getScheme();
        public String getAmountUnit();
       
        /**
         * Getter for property form.
         * @return Value of property form.
         */
        public String getForm();
        
}
