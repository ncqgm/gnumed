/** Java class "available.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.drugref;

import java.util.*;
import java.util.Date;

/**
 * <p>
 * 
 * </p>
 */
public class available {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private Date available_from; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private Date banned; 

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
    private String iso_countrycode; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public product product; 


   ///////////////////////////////////////
   // access methods for associations

    public product getProduct() {
        return product;
    }
    public void setProduct(product _product) {
        if (this.product != _product) {
            if (this.product != null) this.product.removeAvailable(this);
            this.product = _product;
            if (_product != null) _product.addAvailable(this);
        }
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 */
    public Date getAvailable_from() {        
        return available_from;
    } // end getAvailable_from        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setAvailable_from(Date _available_from) {        
        available_from = _available_from;
    } // end setAvailable_from        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public Date getBanned() {        
        return banned;
    } // end getBanned        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setBanned(Date _banned) {        
        banned = _banned;
    } // end setBanned        

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

} // end available





