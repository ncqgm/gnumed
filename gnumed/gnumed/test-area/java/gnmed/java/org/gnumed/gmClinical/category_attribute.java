
/** Java class "category_attribute.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.gnumed.gmClinical;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 *@hibernate.subclass
 *  discriminator-value="c"
 */
public class category_attribute extends clin_attribute {

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public category category; 


   ///////////////////////////////////////
   // access methods for associations

    /** @hibernate.many-to-one
     */
    public category getCategory() {
        return category;
    }
    public void setCategory(category _category) {
        this.category = _category;
    }

} // end category_attribute



