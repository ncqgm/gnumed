/** Java class "Occurence.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.observation;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 *  @hibernate.class
 *      table="occurence"
  *     discriminator-value="o"  
 *  @hibernate.discriminator
 *      column="type"
 *      type="char"
 *      length="2"
 *
 */
public class Occurence {

    /** Holds value of property id. */
    private Long id;    

    /** Getter for property id.
     * @return Value of property id.
     * @hibernate.id
     *  generator-class="hilo.long"
     *      type="long"
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
    
} // end Occurence





