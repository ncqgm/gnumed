/** Java class "subsidies.java" generated from Poseidon for UML.
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
public class subsidies {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private String iso_countrycode; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private String name; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private String comment; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private Integer id; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public Collection subsidized_products = new TreeSet(); // of type subsidized_products


   ///////////////////////////////////////
   // access methods for associations

    public Collection getSubsidized_productss() {
        return subsidized_products;
    }
    public void addSubsidized_products(subsidized_products _subsidized_products) {
        if (! this.subsidized_products.contains(_subsidized_products)) {
            this.subsidized_products.add(_subsidized_products);
            _subsidized_products.setSubsidies(this);
        }
    }
    public void removeSubsidized_products(subsidized_products _subsidized_products) {
        boolean removed = this.subsidized_products.remove(_subsidized_products);
        if (removed) _subsidized_products.setSubsidies((subsidies)null);
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

/**
 * <p>
 * Represents ...
 * </p>
 */
    public String getName() {        
        return name;
    } // end getName        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setName(String _name) {        
        name = _name;
    } // end setName        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public String getComment() {        
        return comment;
    } // end getComment        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setComment(String _comment) {        
        comment = _comment;
    } // end setComment        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public Integer getId() {        
        return id;
    } // end getId        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setId(Integer _id) {        
        id = _id;
    } // end setId        

} // end subsidies





