/*
 * Created on 09-Oct-2004
 *
 */
package org.gnumed.testweb1.data;

/**
 * @author sjtan
 *
 *  
 */
public class EntryMedicationImpl1 extends MedicationImpl1 implements
	EntryMedication {
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
		return item.isEntered();
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

}
