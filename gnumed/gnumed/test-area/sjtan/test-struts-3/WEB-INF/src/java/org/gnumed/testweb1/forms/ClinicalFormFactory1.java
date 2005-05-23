/*
 * ClinicalFormFactory1.java
 *
 * Created on 26 February 2005, 09:19
 */

package org.gnumed.testweb1.forms;

import org.gnumed.testweb1.data.DataObjectFactory;

/**
 *
 * @author sjtan
 */
public class ClinicalFormFactory1 extends AbstractClinicalFormFactory implements IClinicalFormFactory {
   
    /** Creates a new instance of ClinicalFormFactory1 */
    public ClinicalFormFactory1() {
        
        
    }
     
    public BaseClinicalUpdateForm getClinicalUpdateForm() {
        return new ClinicalUpdateForm(getDataObjectFactory(), null);
    }

}
