/*
 * ValidationUtil.java
 *
 * Created on 18 August 2003, 17:56
 */

package quickmed.usecases.test;

/**
 *
 * @author  syan
 */
public class ValidationUtil {
    
    /** Creates a new instance of ValidationUtil */
    public ValidationUtil() {
    }
    
   public static  boolean isBlank(String s) {
        if (s == null || s.trim().length() == 0)
            return true;
        return false;
    }
    
   
}
