/*
 * ShowSysProp.java
 *
 * Created on 26 August 2003, 16:07
 */

package quickmed.usecases.test;

/**
 *
 * @author  syan
 */
public class ShowSysProp {
    
    /** Creates a new instance of ShowSysProp */
    public ShowSysProp() {
    }
    
    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        System.getProperties().list(System.out);
       
    }
    
}
