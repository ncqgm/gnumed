
/** Java class "category.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.gnumed.gmClinical;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 *@hibernate.class
 */
public class category {

  ///////////////////////////////////////
  // attributes


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
    private Long id; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public category_type category_type; 


   ///////////////////////////////////////
   // access methods for associations

    /**
     *@hibernate.many-to-one
     */
    public category_type getCategory_type() {
        return category_type;
    }
    public void setCategory_type(category_type _category_type) {
        if (this.category_type != _category_type) {
            if (this.category_type != null) this.category_type.removeCategory(this);
            this.category_type = _category_type;
            if (_category_type != null) _category_type.addCategory(this);
        }
    }


  ///////////////////////////////////////
  // operations


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
    } // end setName        

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

} // end category



