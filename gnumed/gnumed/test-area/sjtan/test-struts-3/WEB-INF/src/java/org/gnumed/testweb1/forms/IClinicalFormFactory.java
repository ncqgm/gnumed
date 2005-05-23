/*
 * Created on 27-Feb-2005
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
package org.gnumed.testweb1.forms;

import org.gnumed.testweb1.data.DataObjectFactory;

/**
 * @author sjtan
 *
 * TODO To change the template for this generated type comment go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
public interface IClinicalFormFactory {
    /**
     * Getter for property dataObjectFactory.
     * @return Value of property dataObjectFactory.
     */
    public abstract org.gnumed.testweb1.data.DataObjectFactory getDataObjectFactory();

    public abstract void setDataObjectFactory(DataObjectFactory factory);

    public abstract BaseClinicalUpdateForm getClinicalUpdateForm();

    /**
     * @param i
     */
    public abstract void setEntryEpisodeCount(int i);
}