/** Java class "link_country_drug_name.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.drugref;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 */
public class link_country_drug_name {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private String iso_countrycode; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public generic_drug_name generic_drug_name; 


   ///////////////////////////////////////
   // access methods for associations

    public generic_drug_name getGeneric_drug_name() {
        return generic_drug_name;
    }
    public void setGeneric_drug_name(generic_drug_name _generic_drug_name) {
        this.generic_drug_name = _generic_drug_name;
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 */
    public String getIso_countrycode() {        
        return iso_countrycode;
    } // end getIso_countrycode        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setIso_countrycode(String _iso_countrycode) {        
        iso_countrycode = _iso_countrycode;
    } // end setIso_countrycode        

} // end link_country_drug_name





