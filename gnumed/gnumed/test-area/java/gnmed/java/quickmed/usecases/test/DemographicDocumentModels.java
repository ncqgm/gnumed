/*
 * DemographicDocumentModels.java
 *
 * Created on 1 August 2003, 19:53
 */

package quickmed.usecases.test;

import javax.swing.text.*;
/**
 *
 * @author  sjtan
 */
public interface DemographicDocumentModels {
    Document getMedicare();
    Document getPensioner();
    Document getBirthdate();
    Document getLastnames();
    Document getFirstnames();
    
}
