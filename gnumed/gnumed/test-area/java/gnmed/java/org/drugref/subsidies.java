/** Java class "subsidies.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.drugref;

import java.util.*;

/**
 * class that maps to subsidy scheme tables.
 * <p>
 * 
 * </p>
 * @hibernate.class
 * 
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
    public Collection subsidized_products = new java.util.HashSet();
    
    /** Holds value of property audit_id. */
    private Integer audit_id;
    
 // of type subsidized_products


   ///////////////////////////////////////
   // access methods for associations

    /**
//     *@hibernate.set
//     *  inverse="true"
//     *  lazy="true"
//     *@hibernate.collection-key
//     *  column="id_subsidy"
//     *@hibernate.collection-one-to-many
//     *  class="org.drugref.subsidized_products"
     */
    public Collection getSubsidized_productss() {
        return subsidized_products;
    }
    public void addSubsidized_products(subsidized_products _subsidized_products) {
//        Object o = new Object();
//        this.subsidized_products.add(o);
//        this.subsidized_products.remove(o);
        if (! this.subsidized_products.contains(_subsidized_products)) {
            this.subsidized_products.add(_subsidized_products);
            _subsidized_products.setSubsidies(this);
        }
    }
    public void removeSubsidized_products(subsidized_products _subsidized_products) {
        boolean removed = this.subsidized_products.remove(_subsidized_products);
        if (removed) _subsidized_products.setSubsidies((subsidies)null);
    }

    public void setSubsidized_productss(Collection productss) {
          subsidized_products = productss;
    }

  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.property
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
 * Represents the name of the subsidy scheme.
 * </p>
 *  @hibernate.property
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
 * Represents commentary about scheme.
 * </p>
 *  @hibernate.property
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
 * @hibernate.id
 *  generator-class="hilo"
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
    }
    
    /** Getter for property audit_id.
     * @return Value of property audit_id.
     *
     *@hibernate.property
     */
    public Integer getAudit_id() {
        return this.audit_id;
    }
    
    /** Setter for property audit_id.
     * @param audit_id New value of property audit_id.
     *
     */
    public void setAudit_id(Integer audit_id) {
        this.audit_id = audit_id;
    }
    
 // end setId        

} // end subsidies





