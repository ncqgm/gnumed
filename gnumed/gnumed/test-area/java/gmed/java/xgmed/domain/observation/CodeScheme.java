/** Java class "CodeScheme.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package   xgmed.domain.observation;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 * @hibernate.class
 *  table="codeScheme"
 */
public class CodeScheme {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private String idExternal; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private String description; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public Collection coding = new java.util.HashSet();
    
    /** Holds value of property id. */
    private Long id;
    
 // of type Coding


   ///////////////////////////////////////
   // access methods for associations

    /** 
     *
     * custom hbm
     */
    public Collection getCodings() {
        return coding;
    }
    public void addCoding(Coding coding) {
        if (! this.coding.contains(coding)) {
            this.coding.add(coding);
            coding.setCodeScheme(this);
        }
    }
    public void removeCoding(Coding coding) {
        boolean removed = this.coding.remove(coding);
        if (removed) coding.setCodeScheme((CodeScheme)null);
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.property
 */
    public String getIdExternal() {        
        return idExternal;
    } // end getIdExternal        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setIdExternal(String _idExternal) {        
        idExternal = _idExternal;
    } // end setIdExternal        

/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.property
 */
    public String getDescription() {        
        return description;
    } // end getDescription        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setDescription(String _description) {        
        description = _description;
    }
    
    /** Setter for property codings.
     * @param codings New value of property codings.
     *
     */
    public void setCodings(Collection codings) {}
    
    /** Getter for property id.
     * @return Value of property id.
     * @hibernate.id
     *  generator-class="hilo.long"
     *  type="long"
     */
    public Long getId() {
        return this.id;
    }
    
    /** Setter for property id.
     * @param id New value of property id.
     *
     */
    public void setId(Long id) {
        this.id = id;
    }
    
 // end setDescription        

} // end CodeScheme





