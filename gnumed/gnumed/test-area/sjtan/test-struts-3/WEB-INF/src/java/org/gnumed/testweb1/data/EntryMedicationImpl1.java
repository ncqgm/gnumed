/*
 * Created on 09-Oct-2004
 *
 */
package org.gnumed.testweb1.data;
import java.util.HashMap;
import org.gnumed.testweb1.global.Constants;
/**
 * @author sjtan
 *
 *  
 */
public class EntryMedicationImpl1 extends MedicationImpl1 implements
	EntryMedication {
            
        private int index;    
            
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
        
}
