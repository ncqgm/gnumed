/*
 * ShortDateCellRenderer.java
 *
 * Created on 4 August 2003, 08:19
 */

package quickmed.usecases.test;
import javax.swing.table.*;
import javax.swing.*;
import java.util.*;
import javax.swing.text.*;
import java.awt.Component;
import java.text.*;
import java.util.logging.*;

/**
 *
 * @author  sjtan
 */
public class ShortDateCellRenderer extends DefaultTableCellRenderer {
    DateFormat format = DateFormat.getDateInstance(DateFormat.SHORT);
    /** Creates a new instance of ShortDateCellRenderer */
    public ShortDateCellRenderer() {
    }
    
    public Component getTableCellRendererComponent(JTable table, Object value,
                        boolean isSelected, boolean hasFocus, int row, int column)  {
                            Logger.global.info(this + " examining " + value);
        if ( Date.class.isAssignableFrom(value.getClass())  ) {
            try {
                Logger.global.info(this + " set text of " + value + " to " + format.format(value));
                return  super.getTableCellRendererComponent(table,  format.format(value), 
                        isSelected, hasFocus,row,  column) ;
              
            } catch (Exception e) {
                System.err.println(e);
            }
                
        }
        return    super.getTableCellRendererComponent(table,  value,
                        isSelected, hasFocus,row,  column) ;            
    }
    
}
