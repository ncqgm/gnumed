/*
 * Created on 09-Oct-2004
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
package org.gnumed.testweb1.data;
import java.util.List;
import java.util.Map;
import org.gnumed.testweb1.business.ConversionRules;
/**
 * @author sjtan
 *
 * TODO To change the template for this generated type comment go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
public interface EntryMedication extends EntryClinRootItem, Medication {
    public int getIndex();
    public void setIndex(int i);
    
    public Map getSearchParams();
    public void updateDirections();
}
