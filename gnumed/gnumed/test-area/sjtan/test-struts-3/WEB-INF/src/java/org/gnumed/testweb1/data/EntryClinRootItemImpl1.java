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
public class EntryClinRootItemImpl1 extends ClinRootItemImpl1 implements
		EntryClinRootItem {
	ClinWhenEntryAdapter adapter = new ClinWhenEntryAdapter(this);
	
	boolean isLinked, entered;
	String clinWhenString;
	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.ClinWhenEntryHolder#getClinWhenString()
	 */
	public String getClinWhenString() {
		// TODO Auto-generated method stub
		return adapter.getClinWhenString();
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.ClinWhenEntryHolder#setClinWhenString(java.lang.String)
	 */
	public void setClinWhenString(String clinWhenString) {
		// TODO Auto-generated method stub
		adapter.setClinWhenString(clinWhenString);
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.EntryClinRootItem#isEntered()
	 */
	public boolean isEntered() {
		// TODO Auto-generated method stub
		return entered;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.EntryClinRootItem#setEntered(boolean)
	 */
	public void setEntered(boolean entered) {
		// TODO Auto-generated method stub
		this.entered = entered;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.EntryClinRootItem#isLinkedToPreviousEpisode()
	 */
	public boolean isLinkedToPreviousEpisode() {
		// TODO Auto-generated method stub
		return isLinked;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.EntryClinRootItem#setLinkedToPreviousEpisode(boolean)
	 */
	public void setLinkedToPreviousEpisode(boolean linkedToPreviousEpisode) {
		// TODO Auto-generated method stub
		isLinked = linkedToPreviousEpisode;
	}

}
