/** Java class "Names.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.gnumed.gmIdentity;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 *@hibernate.class
 *
 */
public class Names {

  ///////////////////////////////////////
  // attributes

   private StringBuffer sb = new StringBuffer();
/**
 * <p>
 * Represents ...
 * </p>
 */
    private Long id; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private Boolean active; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private String lastnames; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private String firstnames; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private String preferred; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private String title; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public identity identity; 


   ///////////////////////////////////////
   // access methods for associations
///**
// *@hibernate.many-to-one
// */
    public identity getIdentity() {
        return identity;
    }
    public void setIdentity(identity _identity) {
        this.identity = _identity;
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.id
 *      generator-class="hilo"
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
    public Boolean getActive() {        
        return active;
    } // end getActive        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setActive(Boolean _active) {        
        active = _active;
    } // end setActive        

/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.property
 */
    public String getLastnames() {        
        return lastnames;
    } // end getLastnames        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setLastnames(String _lastnames) {        
        lastnames = _lastnames;
    } // end setLastnames        

/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.property
 */
    public String getFirstnames() {        
        return firstnames;
    } // end getFirstnames        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setFirstnames(String _firstnames) {        
        firstnames = _firstnames;
    } // end setFirstnames        

/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.property
 */
    public String getPreferred() {        
        return preferred;
    } // end getPreferred        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setPreferred(String _preferred) {        
        preferred = _preferred;
    } // end setPreferred        

/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.property
 */
    public String getTitle() {        
        return title;
    } // end getTitle        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setTitle(String _title) {        
        title = _title;
    }
    
    public String toString() {
      sb.delete(0, sb.length());
      if (getTitle() != null)
      sb.append(getTitle()).append('.');
      sb.append(getFirstnames());
      sb.append(' ');
      sb.append(getLastnames() );
      return sb.toString();
    }
    
 // end setTitle        

} // end Names





