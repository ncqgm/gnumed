/*
 * ShortDateCellEditor.java
 *
 * Created on 11 August 2003, 11:33
 */

package quickmed.usecases.test;
import java.awt.Component;
import javax.swing.*;
/**
 *
 * @author  sjtan
 */
public class ShortDateCellEditor extends javax.swing.DefaultCellEditor {
    JTextField field;
    Object oldValue;
    static java.text.DateFormat formatter = 
                    java.text.DateFormat.getDateInstance(java.text.DateFormat.SHORT);
    /** Creates a new instance of ShortDateCellEditor */
    public ShortDateCellEditor() {
        super( new JTextField());
    }
    
    public Component getTableCellEditorComponent(JTable table, Object value, boolean isSelected,int row, int column) {
        Component c = super.getTableCellEditorComponent(table, value, isSelected, row, column);
         field = (JTextField) c;
        field.setText(formatter.format(value));
        oldValue = value;
        return field;
    }
    
   public  Object getCellEditorValue() {
        try {
        return formatter.parse(field.getText().trim()) ;
        } catch (Exception e) {
            return oldValue;
         }
    }
}
