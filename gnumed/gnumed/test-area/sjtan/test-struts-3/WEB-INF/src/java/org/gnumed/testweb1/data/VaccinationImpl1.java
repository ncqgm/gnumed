/*
 * Created on 03-Oct-2004
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
public class VaccinationImpl1 extends ClinRootItemImpl1 implements Vaccination {
	public static void setHealthSummary( HealthSummary01 _summary) {
		summary = _summary;
	}
	private static HealthSummary01 summary;
	private String vaccine, batchNo, site, dateGiven;
	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.Vaccination#getVaccine()
	 */
	public Vaccine getVaccine() {
		// TODO Auto-generated method stub
		return summary.findVaccine(getVaccineGiven());
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.Vaccination#getSite()
	 */
	public String getSite() {
		// TODO Auto-generated method stub
		return site;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.Vaccination#setSite(java.lang.String)
	 */
	public void setSite(String site) {
		// TODO Auto-generated method stub
		this.site = site;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.Vaccination#getVaccineGiven()
	 */
	public String getVaccineGiven() {
		// TODO Auto-generated method stub
		return vaccine;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.Vaccination#setVaccineGiven(java.lang.String)
	 */
	public void setVaccineGiven(String shortName) {
		// TODO Auto-generated method stub
		vaccine = shortName;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.Vaccination#getComments()
	 */
	public String getComments() {
		// TODO Auto-generated method stub
		return null;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.Vaccination#setComments(java.lang.String)
	 */
	public void setComments(String descriptiveName) {
		// TODO Auto-generated method stub
		
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.Vaccination#getBatchNo()
	 */
	public String getBatchNo() {
		// TODO Auto-generated method stub
		return batchNo;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.Vaccination#setBatchNo(java.lang.String)
	 */
	public void setBatchNo(String lastBatchNo) {
		// TODO Auto-generated method stub
		this.batchNo = lastBatchNo;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.Vaccination#getDateGivenString()
	 */
	public String getDateGivenString() {
		return dateGiven;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.Vaccination#setDateGivenString(java.lang.String)
	 */
	public void setDateGivenString(String dateGivenString) {
		this.dateGiven  = dateGivenString;
	}

	public String getSoapCat() {
		String s= "p";
		if (!"".equals( super.getSoapCat() )) {
			s = super.getSoapCat();
		}
		return s;
	}
}
