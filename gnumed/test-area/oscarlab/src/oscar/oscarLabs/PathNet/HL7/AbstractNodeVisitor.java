/*
 * Created on 05-Mar-2005
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
package oscar.oscarLabs.PathNet.HL7;

import java.util.Iterator;
import java.util.List;

import oscar.oscarLabs.PathNet.HL7.V2_3.NTE;
import oscar.oscarLabs.PathNet.HL7.V2_3.OBR;
import oscar.oscarLabs.PathNet.HL7.V2_3.OBX;
import oscar.oscarLabs.PathNet.HL7.V2_3.PID;
import oscar.oscarLabs.PathNet.HL7.V2_3.PIDContainer;

/**
 * @author sjtan
 *
 * TODO To change the template for this generated type comment go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
public abstract class AbstractNodeVisitor implements NodeVisitor {

    /* (non-Javadoc)
     * @see oscar.oscarLabs.PathNet.HL7.NodeVisitor#visit(oscar.oscarLabs.PathNet.HL7.Node)
     */
    public void visit(Node node) {
        // TODO Auto-generated method stub
        String[] props = node.getProperties();
        nodeAction(node);
        for (int i =0; i < props.length ; ++i) {
           propertyAction(props[i] , node.get(props[i],"None"));
        }
        postVisitAction(node);
    }

    /**
     * @param node
     */
    public abstract void postVisitAction(Node node) ;

    /**
     * @param node
     */
    public abstract void nodeAction(Node node) ;

    abstract void propertyAction(String s, String value) ;
    /* (non-Javadoc)
     * @see oscar.oscarLabs.PathNet.HL7.NodeVisitor#visitPID(oscar.oscarLabs.PathNet.HL7.V2_3.PID)
     */
    public void visitPID(PID pid) {
        // TODO Auto-generated method stub
        visit(pid);
        List containers = pid.getContainers();
        Iterator i = containers.iterator();
        while (i.hasNext()) {
            PIDContainer container = (PIDContainer) i.next();
            container.accept(this);
        }
        Iterator j = pid.getNotes().iterator();
        while (j.hasNext()) {
            ((Node)j.next()).accept(this);
        }
    }

    /* (non-Javadoc)
     * @see oscar.oscarLabs.PathNet.HL7.NodeVisitor#visitPIDContainer(oscar.oscarLabs.PathNet.HL7.V2_3.PIDContainer)
     */
    public void visitPIDContainer(PIDContainer container) {
        // TODO Auto-generated method stub
        nodeAction(container);
        if (container.getOBR() != null) {
            container.getOBR().accept(this);
        }
        if ( container.getORC()!= null) {
            container.getORC().accept(this);
        }
        
    }

    /* (non-Javadoc)
     * @see oscar.oscarLabs.PathNet.HL7.NodeVisitor#visitOBR(oscar.oscarLabs.PathNet.HL7.V2_3.OBR)
     */
    public void visitOBR(OBR obr) {
        // TODO Auto-generated method stub
        visit(obr);
        Iterator i = obr.getOBXS().iterator();
        while (i.hasNext() ) {
            ((OBX)i.next()).accept(this);
        }
        Iterator j = obr.getNotes().iterator();
        while (j.hasNext() ) {
            ((NTE)j.next()).accept(this);
        }
    }

    /* (non-Javadoc)
     * @see oscar.oscarLabs.PathNet.HL7.NodeVisitor#visitOBX(oscar.oscarLabs.PathNet.HL7.V2_3.OBX)
     */
    public void visitOBX(OBX obx) {
        // TODO Auto-generated method stub
        visit(obx);
    }

}
