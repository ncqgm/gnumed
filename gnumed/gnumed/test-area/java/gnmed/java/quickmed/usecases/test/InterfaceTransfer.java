/*
 * InterfaceTransfer.java
 *
 * Created on 9 August 2003, 06:07
 */

package quickmed.usecases.test;
import java.beans.*;

/**
 *
 * @author  sjtan
 */
public class InterfaceTransfer {
    java.util.logging.Logger logger = java.util.logging.Logger.global;
    PropertyDescriptor[] pds;
    String[] excludes;
    Class aInterface;
    final static Object[] zeroArgs = new Object[0];
    /** Creates a new instance of InterfaceTransfer */
    public InterfaceTransfer( Class c, String[] excludes) throws IntrospectionException {
        this.aInterface = c;
        this.excludes = excludes;
        pds = Introspector.getBeanInfo(c).getPropertyDescriptors();
    }
      
    public void transfer( Object from, Object to) throws Exception {
        if ( ! aInterface.isAssignableFrom(from.getClass())
            || ! aInterface.isAssignableFrom(to.getClass()) )
            throw new ClassCastException("MUST BE OF INTERFACE " + aInterface.getName() );
        
        for (int i = 0; i < pds.length; ++i) {
            if (java.util.Arrays.asList(excludes).contains(pds[i].getName()) )
                continue;
            logger.info("TRANSFERING FROM " + from.getClass() + " TO " + to.getClass() + " USING WRITE METHOD=" +pds[i].getName());
            try {
            logger.info("VALUE OF FROM attribute = " +  pds[i].getReadMethod().invoke(from, zeroArgs ) );
            } catch (Exception e) {
                logger.info(e + " occuring when logging read from " + from);
            }
            try {
                pds[i].getWriteMethod().invoke(
                to, new Object[] { 
                    pds[i].getReadMethod().invoke(
                    from, zeroArgs ) } );
            } catch (Exception e) {
                logger.info(e.toString());
            }
            
        }
    }
    
}
