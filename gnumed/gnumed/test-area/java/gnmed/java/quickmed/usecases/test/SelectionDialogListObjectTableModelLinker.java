/*
 * SelectionDialogListObjectTableModelLinker.java
 *
 * Created on 5 August 2003, 07:15
 */

package quickmed.usecases.test;
import javax.swing.table.*;
import javax.swing.event.*;
import javax.swing.*;
import java.util.*;
import java.util.logging.*;

/**
 *
 * @author  sjtan
 */

/**
 *this is a collaboration class for Dialogs that implement SearchSelectable 
 * and tables that have ListObjectTableModel for their models.
 */
public class SelectionDialogListObjectTableModelLinker implements CellEditorListener {
    
    /** Creates a new instance of SelectionDialogListObjectTableModelLinker */
    public SelectionDialogListObjectTableModelLinker() {
    }
  
        
        /** Holds value of property data. */
        private Object data;
        
        /** Holds value of property model. */
        private ListObjectTableModel model;
        
        /** Holds value of property table. */
        private JTable table;
        
        /** Holds value of property dialog. */
        private JDialog dialog;
        
        public void editingCanceled(ChangeEvent e) {
        }
        
        
        public void editingStopped(ChangeEvent e) {
            initDialog();
            positionAndSizeDialog();
            Object val = getCellEditorValue(e.getSource());
            SearchSelectable dialog = (SearchSelectable) this.dialog;
            if ( val instanceof String)
                dialog.setSearchText((String) val);
            this.dialog.show();
            Logger.global.info( "Dialog selected val = " + dialog.getSelectedItem());
            if ( dialog.getSelectedItem() instanceof String)
                return;
            setValueAtTableCell( dialog.getSelectedItem());
      }
       
        void initDialog() {
            if (dialog == null)
                dialog = new PrescribeDialog(
                (java.awt.Frame) SwingUtilities.getAncestorOfClass(java.awt.Frame.class,
                getTable() ), true );
        }
        
        Object getCellEditorValue(Object source) {
            TableCellEditor ed = ( TableCellEditor) source;
            return  ed.getCellEditorValue();
        }
        
        void positionAndSizeDialog() {
            dialog.setLocation(getTable().getLocationOnScreen());
            dialog.setSize(getTable().getToolkit().getScreenSize().width /2, getTable().getToolkit().getScreenSize().height /2);
        }
        void setValueAtTableCell(Object o)  {
             ((ListObjectTableModel)getTable().getModel()).setValueAt(o);
            setData(((SearchSelectable)dialog).getSelectedItem());
        }
        public void setData(Object data) {
            this.data = data;
        }
     
        /** Getter for property model.
         * @return Value of property model.
         *
         */
        public ListObjectTableModel getModel() {
            return this.model;
        }
        
        /** Setter for property model.
         * @param model New value of property model.
         *
         */
        public void setModel(ListObjectTableModel model) {
            this.model = model;
        }
        
        /** Getter for property table.
         * @return Value of property table.
         *
         */
        public JTable getTable() {
            return this.table;
        }        
   
        /** Setter for property table.
         * @param table New value of property table.
         *
         */
        public void setTable(JTable table) {
            if ( ! (table.getModel() instanceof ListObjectTableModel) )
                throw new RuntimeException( table.getModel() + " must be an instance of ListObjectTableModel");
                this.table = table;
        }
        
        /** Getter for property dialog.
         * @return Value of property dialog.
         *
         */
        public JDialog getDialog() {
            return this.dialog;
        }
        
        /** Setter for property dialog.
         * @param dialog New value of property dialog.
         *
         */
        public void setDialog(JDialog dialog) {
            if (! ( dialog instanceof SearchSelectable)) 
                throw new RuntimeException(dialog + " must implement SearchSelectable");
            this.dialog = dialog;
        }
        
        public void setDialogColumn(String columnName) {
            for ( int i = 0; i < getTable().getModel().getColumnCount() ; ++i) {
                if (columnName.equals( getTable().getModel().getColumnName(i)) ) {
                    setDialogColumn( getTable().getColumnModel().getColumn(i) );
                    return;
                }
            }
        }
        
        public void  setDialogColumn( javax.swing.table.TableColumn column) {
             column.setCellEditor(new DefaultCellEditor(new JTextField())); // so not null next line.
             column.getCellEditor().addCellEditorListener(this);
        }
}
