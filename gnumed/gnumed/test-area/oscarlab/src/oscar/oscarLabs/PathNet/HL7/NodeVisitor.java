/*
 * Created on 05-Mar-2005
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Style - Code Templates
 */
package oscar.oscarLabs.PathNet.HL7;

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
public interface NodeVisitor {

    /**
     * @param node
     */
    void visit(Node node);
    
    void visitPID(PID pid);
    void visitPIDContainer(PIDContainer container);
    void visitOBR(OBR obr);
    void visitOBX(OBX obx);
    

}
