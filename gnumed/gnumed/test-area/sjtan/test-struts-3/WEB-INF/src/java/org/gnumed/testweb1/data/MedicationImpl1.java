/*
 * MedicationImpl1.java
 *
 * Created on September 18, 2004, 7:59 PM
 */

package org.gnumed.testweb1.data;

import java.util.Date;

 
/**
 *
 * @author  sjtan
 */
public class MedicationImpl1 extends ClinRootItemImpl1 implements Medication {
    
    private String brand, generic, shortDescription;
    private java.util.Date last, start, discontinued;
    private int period;
    private double dose;
    private boolean prn, sr;
    private String DB_drug_id, DB_origin;
    private String directions;
    private String ATC;
    
    
    /** Creates a new instance of MedicationImpl1 */
    public MedicationImpl1() {
        last = new java.util.Date();
        start =new java.util.Date();
        
    }
    
    public String getBrandName() {
        return brand;
    }
    
    public String getGenericName() {
        return generic;
    }
    
    public java.util.Date getLast() {
        return last;
    }
    
    public String getShortDescription() {
        return shortDescription;
    }
    
    public java.util.Date getStart() {
        return start;
    }
    
    public void setBrandName(String b) {
        this.brand = b;
    }
    
    public void setGenericName(String n) {
        this.generic = n;
    }
    
    public void setShortDescription(String s) {
        this.shortDescription = s;
    }
    
    public void setStart(java.util.Date s) {
        this.start = s;
    }
    
    public void setLast(java.util.Date l) {
        this.last = l;
    }

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.Medication#getATC_code()
	 */
	public String getATC_code() {
	 	return ATC;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.Medication#setATC_code(java.lang.String)
	 */
	public void setATC_code(String code) {
		 ATC = code;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.Medication#getDB_origin()
	 */
	public String getDB_origin() {
		return DB_origin;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.Medication#setDB_origin(java.lang.String)
	 */
	public void setDB_origin(String origin) {
		 	DB_origin = origin;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.Medication#getDB_drug_id()
	 */
	public String getDB_drug_id() {
		 return DB_drug_id;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.Medication#setDB_drug_id(java.lang.String)
	 */
	public void setDB_drug_id(String id) {
	 	DB_drug_id = id;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.Medication#getDirections()
	 */
	public String getDirections() {
		 return directions;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.Medication#setDirections(java.lang.String)
	 */
	public void setDirections(String directions) {
		 	this.directions = directions;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.Medication#isSR()
	 */
	public boolean isSR() {
		 return sr;
		
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.Medication#setSR(boolean)
	 */
	public void setSR(boolean slowRelease) {
	 	sr = slowRelease;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.Medication#isPRN()
	 */
	public boolean isPRN() {
	 	return prn;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.Medication#setPRN(boolean)
	 */
	public void setPRN(boolean PRN) {
	 	prn = PRN;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.Medication#getDose()
	 */
	public double getDose() {
		return dose;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.Medication#setDose(double)
	 */
	public void setDose(double dose) {
	 	this.dose = dose;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.Medication#getPeriod()
	 */
	public int getPeriod() {
		 return period;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.Medication#setPeriod(int)
	 */
	public void setPeriod(int period) {
	 	this.period = period;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.Medication#getDiscontinued()
	 */
	public Date getDiscontinued() {
		// TODO Auto-generated method stub
		return discontinued;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.Medication#setDiscontinued(java.util.Date)
	 */
	public void setDiscontinued(Date d) {
		// TODO Auto-generated method stub
		this.discontinued = d;
	}
    
}
