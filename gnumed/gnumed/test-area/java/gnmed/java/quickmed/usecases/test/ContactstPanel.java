/*
 * JPanel.java
 *
 * Created on 18 August 2003, 19:21
 */

package quickmed.usecases.test;
import java.util.*;
import java.util.logging.*;
import javax.swing.tree.*;
import javax.swing.*;
import org.gnumed.gmIdentity.identity_role;

/**
 *
 * @author  syan
 */
public class ContactstPanel extends javax.swing.JPanel {
    final static String BUNDLE=Globals.BUNDLE;
    final static String CREATE_ROLE=Globals.CREATE_ROLE;
    /** Creates new form JPanel */
    public ContactstPanel() {
        initComponents();
        setTabLabels();
        try {
            createProviderModel();
        } catch (Exception e) {
            e.printStackTrace();
        }
        jList2.setModel(new DefaultListModel());
        
        ToolTipManager.sharedInstance().setEnabled(true);
        
    }
    
    void setTabLabels() {
        jTabbedPane1.setTitleAt(2, getResourceName("create_role"));
        
        jTabbedPane1.setTitleAt(1, getResourceName("create_provider"));
        jTabbedPane1.setTitleAt(0, getResourceName("find_provider"));
        
        
    }
    
    String getResourceName(String key) {
        return  ResourceBundle.getBundle(BUNDLE).getString(key);
    }
    
    identity_role createRole( String name, identity_role[] directSuperclasses) {
        identity_role role = new identity_role();
        role.setName(name);
        if (directSuperclasses == null)
            return role;
        for (int i = 0; i < directSuperclasses.length; ++i) {
            role.addSuperType(directSuperclasses[i]);
        }
        return role;
    }
    
    DefaultMutableTreeNode top = new DefaultMutableTreeNode(createRole(getResourceName("Providers") , null));
    identity_role[] supers = new identity_role[] { (identity_role) top.getUserObject() };
    DefaultMutableTreeNode specialists = new DefaultMutableTreeNode( createRole( getResourceName("specialists"), supers) );
    DefaultMutableTreeNode gps = new DefaultMutableTreeNode( createRole(getResourceName("gps"), supers) , true );
    identity_role[] specialistSuper = new identity_role[] { (identity_role) specialists.getUserObject() };
    DefaultMutableTreeNode obstetricians = new DefaultMutableTreeNode( createRole( getResourceName("obstetricians"), specialistSuper) , true );
    DefaultMutableTreeNode surgeons = new DefaultMutableTreeNode( createRole( getResourceName("surgeons"), specialistSuper) );
    DefaultMutableTreeNode physicians = new DefaultMutableTreeNode( createRole( getResourceName("physicians"), specialistSuper) );
    DefaultMutableTreeNode psychs = new DefaultMutableTreeNode( createRole( getResourceName("psychiatrists"), specialistSuper) , true );
    
    identity_role[] surgeonSuper = new identity_role[] { (identity_role) surgeons.getUserObject() };
    identity_role[] physicianSuper = new identity_role[] { (identity_role) physicians.getUserObject() };
    DefaultMutableTreeNode generalSurgeons = new DefaultMutableTreeNode( createRole( getResourceName("general_surgeons"), surgeonSuper) , true );
    DefaultMutableTreeNode generalPhysicians = new DefaultMutableTreeNode( createRole( getResourceName("general_physicians"), physicianSuper), true  );
    DefaultMutableTreeNode ent = new DefaultMutableTreeNode( createRole( getResourceName("ent_surgeons"), surgeonSuper), true  );
    DefaultMutableTreeNode plastics = new DefaultMutableTreeNode( createRole( getResourceName("plastics"), surgeonSuper), true  );
    DefaultMutableTreeNode dermatologists = new DefaultMutableTreeNode( createRole( getResourceName("dermatologists"), physicianSuper) , true );
    DefaultMutableTreeNode paediatricians = new DefaultMutableTreeNode( createRole( getResourceName("paediatricians"), physicianSuper), true  );
    DefaultMutableTreeNode paedsurgs = new DefaultMutableTreeNode( createRole( getResourceName("paediatric_surgeons"), surgeonSuper) , true );
    DefaultMutableTreeNode cardiologist = new DefaultMutableTreeNode( createRole( getResourceName("cardiologists"), physicianSuper), true  );
    DefaultMutableTreeNode orthopods = new DefaultMutableTreeNode( createRole( getResourceName("orthopaedic_surgeons"), surgeonSuper), true  );
    DefaultMutableTreeNode eyedocs = new DefaultMutableTreeNode( createRole( getResourceName("opthalmologists"), surgeonSuper), true  );
    DefaultMutableTreeNode urologists = new DefaultMutableTreeNode( createRole( getResourceName("urologists"), surgeonSuper), true );
    void createProviderModel() {
        top.add(specialists);
        top.add(gps);
        specialists.add(surgeons);
        specialists.add(physicians);
        specialists.add(obstetricians);
        specialists.add(psychs);
        physicians.add(generalPhysicians);
        physicians.add(dermatologists);
        physicians.add(cardiologist);
        physicians.add(paediatricians);
        surgeons.add(generalSurgeons);
        surgeons.add(orthopods);
        surgeons.add(eyedocs);
        surgeons.add(urologists);
        surgeons.add(paedsurgs);
        surgeons.add(plastics);
        jTree1.setModel(new DefaultTreeModel(top));
        jTree3.setModel( new DefaultTreeModel(top));
        
        
    }
    
    /** This method is called from within the constructor to
     * initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is
     * always regenerated by the Form Editor.
     */
    private void initComponents() {//GEN-BEGIN:initComponents
        java.awt.GridBagConstraints gridBagConstraints;

        jPopupMenu1 = new javax.swing.JPopupMenu();
        jMenuItem1 = new javax.swing.JMenuItem();
        jTabbedPane1 = new javax.swing.JTabbedPane();
        jPanel2 = new javax.swing.JPanel();
        jLabel2 = new javax.swing.JLabel();
        jTextField2 = new javax.swing.JTextField();
        jLabel3 = new javax.swing.JLabel();
        jComboBox1 = new javax.swing.JComboBox();
        jButton3 = new javax.swing.JButton();
        jLabel4 = new javax.swing.JLabel();
        jScrollPane2 = new javax.swing.JScrollPane();
        jList1 = new javax.swing.JList();
        jButton5 = new javax.swing.JButton();
        jPanel3 = new javax.swing.JPanel();
        jPanel5 = new javax.swing.JPanel();
        jLabel5 = new javax.swing.JLabel();
        lastNamesjTextField3 = new javax.swing.JTextField();
        jLabel6 = new javax.swing.JLabel();
        firstNamesjTextField4 = new javax.swing.JTextField();
        jLabel9 = new javax.swing.JLabel();
        addressjTextField5 = new javax.swing.JTextField();
        jLabel10 = new javax.swing.JLabel();
        telephonejTextField6 = new javax.swing.JTextField();
        jLabel11 = new javax.swing.JLabel();
        faxjTextField7 = new javax.swing.JTextField();
        jLabel7 = new javax.swing.JLabel();
        commentText = new javax.swing.JTextArea();
        jPanel4 = new javax.swing.JPanel();
        jScrollPane3 = new javax.swing.JScrollPane();
        jList2 = new javax.swing.JList();
        jScrollPane4 = new javax.swing.JScrollPane();
        jTree3 = new javax.swing.JTree();
        jButton4 = new javax.swing.JButton();
        jLabel8 = new javax.swing.JLabel();
        jSeparator1 = new javax.swing.JSeparator();
        jLabel12 = new javax.swing.JLabel();
        jPanel1 = new javax.swing.JPanel();
        jLabel1 = new javax.swing.JLabel();
        jTextField1 = new javax.swing.JTextField();
        jCheckBox1 = new javax.swing.JCheckBox();
        jScrollPane1 = new javax.swing.JScrollPane();
        jTree1 = new javax.swing.JTree();
        jButton1 = new javax.swing.JButton();
        jButton2 = new javax.swing.JButton();

        jMenuItem1.setMnemonic('a');
        jMenuItem1.setText("add role");
        jPopupMenu1.add(jMenuItem1);

        setLayout(new java.awt.BorderLayout());

        jPanel2.setLayout(new java.awt.GridBagLayout());

        jLabel2.setText("Lastname, Firstname");
        jPanel2.add(jLabel2, new java.awt.GridBagConstraints());

        jTextField2.setText("jTextField2");
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        gridBagConstraints.weightx = 1.0;
        jPanel2.add(jTextField2, gridBagConstraints);

        jLabel3.setText("role");
        jPanel2.add(jLabel3, new java.awt.GridBagConstraints());

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        jPanel2.add(jComboBox1, gridBagConstraints);

        jButton3.setText("find");
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        gridBagConstraints.anchor = java.awt.GridBagConstraints.WEST;
        gridBagConstraints.weightx = 1.0;
        jPanel2.add(jButton3, gridBagConstraints);

        jLabel4.setText("results");
        jPanel2.add(jLabel4, new java.awt.GridBagConstraints());

        jScrollPane2.setViewportView(jList1);

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.fill = java.awt.GridBagConstraints.BOTH;
        gridBagConstraints.weightx = 1.0;
        gridBagConstraints.weighty = 1.0;
        jPanel2.add(jScrollPane2, gridBagConstraints);

        jButton5.setText("edit");
        jButton5.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jButton5ActionPerformed(evt);
            }
        });

        jPanel2.add(jButton5, new java.awt.GridBagConstraints());

        jTabbedPane1.addTab("tab2", jPanel2);

        jPanel3.setLayout(new java.awt.GridBagLayout());

        jPanel5.setLayout(new java.awt.GridBagLayout());

        jLabel5.setText("Last names");
        jPanel5.add(jLabel5, new java.awt.GridBagConstraints());

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = 3;
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        jPanel5.add(lastNamesjTextField3, gridBagConstraints);

        jLabel6.setText("Firstnames");
        jPanel5.add(jLabel6, new java.awt.GridBagConstraints());

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        gridBagConstraints.anchor = java.awt.GridBagConstraints.WEST;
        jPanel5.add(firstNamesjTextField4, gridBagConstraints);

        jLabel9.setText("address");
        jPanel5.add(jLabel9, new java.awt.GridBagConstraints());

        addressjTextField5.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                addressjTextField5ActionPerformed(evt);
            }
        });

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        gridBagConstraints.weightx = 1.0;
        jPanel5.add(addressjTextField5, gridBagConstraints);

        jLabel10.setText("telephone");
        jPanel5.add(jLabel10, new java.awt.GridBagConstraints());

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        gridBagConstraints.weightx = 1.0;
        jPanel5.add(telephonejTextField6, gridBagConstraints);

        jLabel11.setText("fax");
        jPanel5.add(jLabel11, new java.awt.GridBagConstraints());

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        gridBagConstraints.weightx = 2.0;
        jPanel5.add(faxjTextField7, gridBagConstraints);

        jLabel7.setText("comments");
        jPanel5.add(jLabel7, new java.awt.GridBagConstraints());

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        gridBagConstraints.fill = java.awt.GridBagConstraints.BOTH;
        jPanel5.add(commentText, gridBagConstraints);

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        jPanel3.add(jPanel5, gridBagConstraints);

        jPanel4.setLayout(new java.awt.GridLayout(1, 0));

        jPanel4.setToolTipText(java.util.ResourceBundle.getBundle("SummaryTerms").getString("provider_tree_command"));
        jScrollPane3.setViewportView(jList2);

        jPanel4.add(jScrollPane3);

        jTree3.setToolTipText("shift left selects into the list, shift-right deletes from the list");
        jTree3.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyPressed(java.awt.event.KeyEvent evt) {
                jTree3KeyPressed(evt);
            }
        });
        jTree3.addMouseListener(new java.awt.event.MouseAdapter() {
            public void mousePressed(java.awt.event.MouseEvent evt) {
                checkForPopup(evt);
            }
        });

        jScrollPane4.setViewportView(jTree3);

        jPanel4.add(jScrollPane4);

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = 4;
        gridBagConstraints.fill = java.awt.GridBagConstraints.BOTH;
        gridBagConstraints.weightx = 2.0;
        gridBagConstraints.weighty = 2.0;
        jPanel3.add(jPanel4, gridBagConstraints);

        jButton4.setText("add provider");
        jButton4.setToolTipText("add the providerwith the listed roles");
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        jPanel3.add(jButton4, gridBagConstraints);

        jLabel8.setText("occupied roles");
        jPanel3.add(jLabel8, new java.awt.GridBagConstraints());

        jSeparator1.setOrientation(javax.swing.SwingConstants.VERTICAL);
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = 2;
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        gridBagConstraints.weightx = 1.0;
        jPanel3.add(jSeparator1, gridBagConstraints);

        jLabel12.setText(java.util.ResourceBundle.getBundle("SummaryTerms").getString("provider_tree_command"));
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        gridBagConstraints.anchor = java.awt.GridBagConstraints.WEST;
        jPanel3.add(jLabel12, gridBagConstraints);

        jTabbedPane1.addTab("tab3", jPanel3);

        jPanel1.setLayout(new java.awt.GridBagLayout());

        jLabel1.setText("category");
        jPanel1.add(jLabel1, new java.awt.GridBagConstraints());

        jTextField1.setColumns(20);
        jTextField1.setText("jTextField1");
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        gridBagConstraints.weightx = 1.0;
        jPanel1.add(jTextField1, gridBagConstraints);

        jCheckBox1.setText("is subcategory of");
        jCheckBox1.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jCheckBox1ActionPerformed(evt);
            }
        });

        jPanel1.add(jCheckBox1, new java.awt.GridBagConstraints());

        jTree1.addMouseListener(new java.awt.event.MouseAdapter() {
            public void mousePressed(java.awt.event.MouseEvent evt) {
                checkForPopup(evt);
            }
        });

        jScrollPane1.setViewportView(jTree1);

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        gridBagConstraints.fill = java.awt.GridBagConstraints.BOTH;
        gridBagConstraints.weighty = 2.0;
        jPanel1.add(jScrollPane1, gridBagConstraints);

        jButton1.setText("add category");
        jPanel1.add(jButton1, new java.awt.GridBagConstraints());

        jButton2.setText("remove category");
        jPanel1.add(jButton2, new java.awt.GridBagConstraints());

        jTabbedPane1.addTab("tab1", jPanel1);

        add(jTabbedPane1, java.awt.BorderLayout.CENTER);

    }//GEN-END:initComponents

    private void addressjTextField5ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_addressjTextField5ActionPerformed
        // Add your handling code here:
    }//GEN-LAST:event_addressjTextField5ActionPerformed
    
    private void jTree3KeyPressed(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_jTree3KeyPressed
        // Add your handling code here:
        
        if ( evt.getKeyCode() == evt.VK_LEFT && ( evt.getModifiersEx() & evt.SHIFT_DOWN_MASK ) != 0  )
            addSelectedRoleInTreeToList();
        else
            if (evt.getKeyCode() == evt.VK_RIGHT && ( evt.getModifiersEx() & evt.SHIFT_DOWN_MASK) != 0  )
                deleteSelectedRoleInTreeFromList();
       
    }//GEN-LAST:event_jTree3KeyPressed
    
    private void checkForPopup(java.awt.event.MouseEvent evt) {//GEN-FIRST:event_checkForPopup
        // Add your handling code here:
        if (evt.isPopupTrigger()) {
            
            jPopupMenu1.show((java.awt.Component)evt.getSource(), evt.getX(), evt.getY());
        }
    }//GEN-LAST:event_checkForPopup
    
    private void jButton5ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jButton5ActionPerformed
        // Add your handling code here:
    }//GEN-LAST:event_jButton5ActionPerformed
    
    private void jCheckBox1ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jCheckBox1ActionPerformed
        // Add your handling code here:
    }//GEN-LAST:event_jCheckBox1ActionPerformed
    
    
    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JTextField addressjTextField5;
    private javax.swing.JTextArea commentText;
    private javax.swing.JTextField faxjTextField7;
    private javax.swing.JTextField firstNamesjTextField4;
    private javax.swing.JButton jButton1;
    private javax.swing.JButton jButton2;
    private javax.swing.JButton jButton3;
    private javax.swing.JButton jButton4;
    private javax.swing.JButton jButton5;
    private javax.swing.JCheckBox jCheckBox1;
    private javax.swing.JComboBox jComboBox1;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel10;
    private javax.swing.JLabel jLabel11;
    private javax.swing.JLabel jLabel12;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JLabel jLabel3;
    private javax.swing.JLabel jLabel4;
    private javax.swing.JLabel jLabel5;
    private javax.swing.JLabel jLabel6;
    private javax.swing.JLabel jLabel7;
    private javax.swing.JLabel jLabel8;
    private javax.swing.JLabel jLabel9;
    private javax.swing.JList jList1;
    private javax.swing.JList jList2;
    private javax.swing.JMenuItem jMenuItem1;
    private javax.swing.JPanel jPanel1;
    private javax.swing.JPanel jPanel2;
    private javax.swing.JPanel jPanel3;
    private javax.swing.JPanel jPanel4;
    private javax.swing.JPanel jPanel5;
    private javax.swing.JPopupMenu jPopupMenu1;
    private javax.swing.JScrollPane jScrollPane1;
    private javax.swing.JScrollPane jScrollPane2;
    private javax.swing.JScrollPane jScrollPane3;
    private javax.swing.JScrollPane jScrollPane4;
    private javax.swing.JSeparator jSeparator1;
    private javax.swing.JTabbedPane jTabbedPane1;
    private javax.swing.JTextField jTextField1;
    private javax.swing.JTextField jTextField2;
    private javax.swing.JTree jTree1;
    private javax.swing.JTree jTree3;
    private javax.swing.JTextField lastNamesjTextField3;
    private javax.swing.JTextField telephonejTextField6;
    // End of variables declaration//GEN-END:variables
    
    
    void addSelectedRoleInTreeToList() {
        Logger.global.info("  ** ");
        templateTreeToListAction(jTree3, jList2, "addElement", false);
    }
    
    void deleteSelectedRoleInTreeFromList() {
         Logger.global.info("  ** ");
        templateTreeToListAction(jTree3, jList2, "removeElement" , true);
    }
    
    void templateTreeToListAction( JTree tree, JList list, String methodName, boolean shouldContain ) {
        TreePath[] paths = tree.getSelectionPaths();
        for (int i =0; i < paths.length; ++i) {
            if ( paths[i].getLastPathComponent() instanceof DefaultMutableTreeNode) {
                DefaultMutableTreeNode node = (DefaultMutableTreeNode) paths[i].getLastPathComponent();
                DefaultListModel model = (DefaultListModel) list.getModel();
                boolean condition = model.contains(node.getUserObject());
                
                if ( condition && shouldContain || ( !condition && !shouldContain) ) {
                    try {
                    DefaultListModel.class.getMethod(methodName, new Class[] { Object.class } )
                    .invoke( model, new Object[] { node.getUserObject() });
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }
            }
        }
        
    }
    
    
    
    
}
