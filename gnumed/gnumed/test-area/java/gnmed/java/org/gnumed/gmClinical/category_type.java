
/** Java class "category_type.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.gnumed.gmClinical;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 * such as ethnicity,marital status
 *
 *@hibernate.class
 *  discriminator-value="c"
 *
 *@hibernate.discriminator
 *  column="type"
 *  type="string"
 *  length="2"
 */
public class category_type {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 * 
 */
    private Long id; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private String name; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public Collection category = new java.util.HashSet(); // of type category


   ///////////////////////////////////////
   // access methods for associations

    /**
     *@hibernate.set
     *  lazy="false"
     *@hibernate.collection-key
     *  column="category"
     *@hibernate.collection-one-to-many
     *  class="org.gnumed.gmClinical.category"
     */
    public Collection getCategorys() {
        return category;
    }
    public void addCategory(category _category) {
        if (! this.category.contains(_category)) {
            this.category.add(_category);
            _category.setCategory_type(this);
        }
    }
    public void removeCategory(category _category) {
        boolean removed = this.category.remove(_category);
        if (removed) _category.setCategory_type((category_type)null);
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.id
 *  generator-class="hilo"
 */
    public Long getId() {        
        return id;
    } // end getId        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setId(Long _id) {        
        id = _id;
    } // end setId        

/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.property
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
    }
    
    /** Setter for property categorys.
     * @param categorys New value of property categorys.
     *
     */
    public void setCategorys(Collection categorys) {
        category = categorys;
    }
    
    public boolean equals(Object o) {
        if ( ! ( o instanceof category_type))
            return super.equals(o);
        return getId().equals( ((category_type)o).getId());
    }
 // end setName        

} // end category_type



