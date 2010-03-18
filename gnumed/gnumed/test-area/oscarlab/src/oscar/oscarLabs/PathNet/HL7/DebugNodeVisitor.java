/*
 * Created on 05-Mar-2005
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
package oscar.oscarLabs.PathNet.HL7;

/**
 * @author sjtan
 *
 * TODO To change the template for this generated type comment go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
public class DebugNodeVisitor extends AbstractNodeVisitor {

    /* (non-Javadoc)
     * @see oscar.oscarLabs.PathNet.HL7.AbstractNodeVisitor#postVisitAction(oscar.oscarLabs.PathNet.HL7.Node)
     */
    public void postVisitAction(Node node) {
        // TODO Auto-generated method stub
        System.err.println();
    }

    /* (non-Javadoc)
     * @see oscar.oscarLabs.PathNet.HL7.AbstractNodeVisitor#nodeAction(oscar.oscarLabs.PathNet.HL7.Node)
     */
    public void nodeAction(Node node) {
        // TODO Auto-generated method stub
        System.err.println(node.toString());
    }

    /* (non-Javadoc)
     * @see oscar.oscarLabs.PathNet.HL7.AbstractNodeVisitor#propertyAction(java.lang.String, java.lang.String)
     */
    void propertyAction(String s, String value) {
        // TODO Auto-generated method stub
        System.err.println(s + ":" + value);
    }
    
}
