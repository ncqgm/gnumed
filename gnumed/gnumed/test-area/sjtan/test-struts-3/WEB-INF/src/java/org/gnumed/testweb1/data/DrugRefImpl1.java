/*
 * Created on 12-Oct-2004
 *
 */
package org.gnumed.testweb1.data;
import java.sql.ResultSet;
/**
 * @author sjtan
 *
 */
public class DrugRefImpl1 implements DrugRef, DrugRefConstructed {
    
    	String brandName, atc_code, atc_name;
	String description;
	int subsidizedRepeats, subsidizedQty, packageSize;
	Integer id;
	String routeAbbrev;
	String scheme, form, amountUnit;
	 
	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.DrugRef#getBrandName()
	 */
	public String getBrandName() {
		 return brandName;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.DrugRef#getATC_code()
	 */
	public String getATC_code() {
		 return atc_code;
		
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.DrugRef#getATC()
	 */
	public String getATC() {
		return atc_name;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.DrugRef#getDescription()
	 */
	public String getDescription() {
		return description;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.DrugRef#getSubsidizedRepeats()
	 */
	public int getSubsidizedRepeats() {
	 return subsidizedRepeats;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.DrugRef#getSubsidizedQuantity()
	 */
	public int getSubsidizedQuantity() {
		return subsidizedQty;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.DrugRef#getDefaultRepeats()
	 */
	public int getDefaultRepeats() {
		 return subsidizedRepeats;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.DrugRef#getDefaultQuantity()
	 */
	public int getDefaultQuantity() {
		 return subsidizedQty;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.DrugRef#getId()
	 */
	public Integer getId() {
		return id;
	}
	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.DrugRef#getPackageSize()
	 */
	public int getPackageSize() {
		return packageSize;
	}
	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.DrugRef#getRouteAbbrev()
	 */
	public String getRouteAbbrev() {
		return routeAbbrev;
	}
	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.DrugRef#getScheme()
	 */
	public String getScheme() {
		return scheme;
	}
	

        public String getForm() {
            return form;
        }
        
        /* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.DrugRefConstructed#setAttributes(java.lang.Integer, java.lang.String, java.lang.String, java.lang.String, java.lang.String, int, int, int)
	 */
	public void setAttributes(Integer id, String brandName, String atc, String atc_code, String description, int qty, int rpts, int pkg_size, String scheme, String form,  String amountUnit) {
		this.id = id;
		this.brandName = brandName;
		this.atc_code = atc_code;
		this.atc_name = atc;
		this.description = description;
		this.subsidizedQty= qty;
		this.subsidizedRepeats = rpts;
		this.scheme = scheme;
                this.form = form;
                this.amountUnit = amountUnit;
	}
        
        public String getAmountUnit() {
            return amountUnit;
        }
        
}
