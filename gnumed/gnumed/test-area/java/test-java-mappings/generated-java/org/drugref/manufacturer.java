/** Java class "manufacturer.java" generated from Poseidon for UML.
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
public class manufacturer {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private String address; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private String phone; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private String fax; 

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
    private String code; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private Stringt name; 

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
    public Collection link_product_manufacturer = new TreeSet(); // of type link_product_manufacturer


   ///////////////////////////////////////
   // access methods for associations

    public Collection getLink_product_manufacturers() {
        return link_product_manufacturer;
    }
    public void addLink_product_manufacturer(link_product_manufacturer _link_product_manufacturer) {
        if (! this.link_product_manufacturer.contains(_link_product_manufacturer)) {
            this.link_product_manufacturer.add(_link_product_manufacturer);
            _link_product_manufacturer.setManufacturer(this);
        }
    }
    public void removeLink_product_manufacturer(link_product_manufacturer _link_product_manufacturer) {
        boolean removed = this.link_product_manufacturer.remove(_link_product_manufacturer);
        if (removed) _link_product_manufacturer.setManufacturer((manufacturer)null);
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 */
    public String getAddress() {        
        return address;
    } // end getAddress        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setAddress(String _address) {        
        address = _address;
    } // end setAddress        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public String getPhone() {        
        return phone;
    } // end getPhone        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setPhone(String _phone) {        
        phone = _phone;
    } // end setPhone        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public String getFax() {        
        return fax;
    } // end getFax        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setFax(String _fax) {        
        fax = _fax;
    } // end setFax        

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
    public String getCode() {        
        return code;
    } // end getCode        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setCode(String _code) {        
        code = _code;
    } // end setCode        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public manufacturer.Stringt getName() {        
        return name;
    } // end getName        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setName(manufacturer.Stringt _name) {        
        name = _name;
    } // end setName        

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


  ///////////////////////////////////////
  // inner classes/interfaces

/**
 * <p>
 * 
 * </p>
 */
public class Stringt {
} // end manufacturer.Stringt

} // end manufacturer





