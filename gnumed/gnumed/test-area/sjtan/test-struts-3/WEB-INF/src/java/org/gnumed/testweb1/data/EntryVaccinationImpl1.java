 
package org.gnumed.testweb1.data;
import org.gnumed.testweb1.global.Util;
/**
 * @author sjtan
 */
public class EntryVaccinationImpl1
 extends VaccinationImpl1 implements
	EntryVaccination, ClinWhenHolder {

	EntryClinRootItem item = new EntryClinRootItemImpl1();
	ClinWhenEntryAdapter adapter = new ClinWhenEntryAdapter(this);
	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.ClinWhenEntryHolder#getClinWhenString()
	 */
	public String getClinWhenString() {
		return adapter.getClinWhenString();
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.ClinWhenEntryHolder#setClinWhenString(java.lang.String)
	 */
	public void setClinWhenString(String clinWhenString) {
		adapter.setClinWhenString(clinWhenString);
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

	public String getVaccineGiven() {
		 return Util.nullIsBlank( super.getVaccineGiven() );
	}
	
	public String getNarrative() {
		String n = Util.nullIsBlank(super.getNarrative());
		return n;
	}
	
	public void setVaccineGiven(String vaccineGiven) {
		vaccineGiven = Util.nullIsBlank(vaccineGiven);
		if ("".equals(vaccineGiven) || "0".equals(vaccineGiven) ) {
			setEntered(false);
		} else {
			setEntered(true);
		}
		super.setVaccineGiven(vaccineGiven);
		
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.EntryClinRootItem#isEntered()
	 */
	public boolean isEntered() {
		return item.isEntered();
	}
	
}
