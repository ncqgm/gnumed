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
public abstract class AbstractClinicalFormFactory implements
        IClinicalFormFactory {

    private DataObjectFactory objectFactory;
    
    int entryEpisodeCount;
    
    public  void setEntryEpisodeCount(int i) {
        entryEpisodeCount =i;
    }
    
    /**
     * Getter for property dataObjectFactory.
     * @return Value of property dataObjectFactory.
     */
    public org.gnumed.testweb1.data.DataObjectFactory getDataObjectFactory() {
        return objectFactory;
    }
    
    public void setDataObjectFactory( DataObjectFactory factory) {
        this.objectFactory = factory;
    }

    /**
     * @return
     */
    protected int GetEntryEpisodeCount() {
        // TODO Auto-generated method stub
        return entryEpisodeCount;
    }
    

}
