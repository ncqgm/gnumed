/*
 * DrugComboBoxA.java
 *
 * Created on 5 August 2003, 00:11
 */

package quickmed.usecases.test;
import java.util.*;
import javax.swing.*;

/**
 *
 * @author  sjtan
 */
public class DrugComboBoxA extends javax.swing.JComboBox {
    TestScriptDrugManager manager = new TestScriptDrugManager();
    /** Creates a new instance of DrugComboBoxA */
    public DrugComboBoxA() {
        super();
        addActionListener( new java.awt.event.ActionListener () {
            public void actionPerformed(java.awt.event.ActionEvent e) {
                jComboBox1ActionSearchProduct(e);
            }
        });
        setEditable(true);
    }
      private void jComboBox1ActionSearchProduct(java.awt.event.ActionEvent evt) {
        // Add your handling code here:
        System.out.println(evt.getActionCommand());
        
        System.out.println("Selected item = " + getSelectedItem());
        try {
            if (!(  getSelectedItem() instanceof String))
                return;
            List l = manager.findPackagedProductByDrugName((String)   getSelectedItem());
            l.add(0,   getSelectedItem());
              setModel(new DefaultComboBoxModel( l.toArray()));
            
              //setPopupVisible(true);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
