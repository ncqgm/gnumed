/*
 * PrintVisitor.java
 *
 * Created on 11 July 2003, 02:23
 */

package xgmed.helper;

/**
 *
 * @author  sjtan
 */
public class PrintVisitor extends AbstractVisitor {
    
    /** Creates a new instance of PrintVisitor */
    public PrintVisitor() {
    }
    
    void nodeAction(Visitable v) {
        System.out.println(v);
    }
    
}
