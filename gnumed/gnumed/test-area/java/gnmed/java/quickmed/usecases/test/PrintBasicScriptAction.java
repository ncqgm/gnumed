/*
 * PrintBasicScriptAction.java
 *
 * Created on 2 September 2003, 23:40
 */

package quickmed.usecases.test;
import javax.swing.*;
import java.util.*;
import java.util.logging.*;
import org.gnumed.gmClinical.*;
/**
 *
 * @author  syan
 */
public class PrintBasicScriptAction extends AbstractAction {
    JTable table;
    
    /** Creates a new instance of PrintBasicScriptAction */
    public PrintBasicScriptAction(JTable table) {
        super( Globals.bundle.getString("print_script") );
        
        this.table = table;
        
        
    }
    
    public void actionPerformed(java.awt.event.ActionEvent e) {
        ListSelectionModel listModel = table.getSelectionModel();
        List list = new ArrayList();
        Logger.global.info("table.model = " + table.getModel());
        if ( table.getModel() instanceof ListObjectTableModel )  {
            ListObjectTableModel model = (ListObjectTableModel) table.getModel();
            for (int i =0; i < model.getList().size() ; ++i) {
                
                Object o  = model.getList().get(i);
                Logger.global.info("List object  = " + o + " is DrugListView " + (o instanceof DrugListView ));
                if (o instanceof DrugListView) {
                    DrugListView view = (DrugListView) o;
                    Logger.global.info("view selected = " + view);
                    if ( view.isPrint()) {
                        link_script_drug lsd = new link_script_drug();
                        lsd.setScript_drug(((DummyDrugListView)view).getScriptDrug());
                        lsd.setRepeats(view.getRepeats());
                        list.add(lsd);
                    }
                }
                
            }
            java.awt.Container c = SwingUtilities.getAncestorOfClass(IdentityHolder.class, table);
            if (c != null) {
                IdentityHolder holder = (IdentityHolder) c;
                TestPrintPreviewInnerFrame frame = new TestPrintPreviewInnerFrame( holder.getIdentity(), list);
                // an assumption that desktop is an ancestor of table
                java.awt.Container desktop = SwingUtilities.getAncestorOfClass(JDesktopPane.class, table);
                desktop.add(frame);
                frame.setVisible(true);
            }
        }
        
        
        
        
    }
    
}
