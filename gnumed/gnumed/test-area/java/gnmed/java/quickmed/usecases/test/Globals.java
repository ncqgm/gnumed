/*
 * Globals.java
 *
 * Created on 18 August 2003, 20:25
 */

package quickmed.usecases.test;
import java.util.*;
/**
 *
 * @author  syan
 */
public class Globals {
    public static final String BUNDLE = "SummaryTerms";
    public static final String CUSTOM_PROPERTIES_FILE = "gnmed-test.properties";
    public static final String  CREATE_ROLE = "create_role";
    /** Creates a new instance of Globals */
    public Globals() {
    }
    
    public static final ResourceBundle bundle = ResourceBundle.getBundle(BUNDLE);
}
