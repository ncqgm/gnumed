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
import org.gnumed.gmIdentity.*;

/**
 *
 * @author  syan
 */
public class ContactsPanel extends javax.swing.JPanel implements ProviderView{
    final static String BUNDLE=Globals.BUNDLE;
    final static String CREATE_ROLE=Globals.CREATE_ROLE;
    
    private ProviderController controller;
    
    private Collection removed = new HashSet();
    
    
    
    
    /** Creates new form JPanel */
    public ContactsPanel() {
        initComponents();
        setTabLabels();
        setSexComboLabels();
        jList2.setModel(new DefaultListModel());
        
        ToolTipManager.sharedInstance().setEnabled(true);
        configure();
    }
    
    void configure() {
        identity id = new identity();
        ManagerReference manager = new SingleSessionManagerReference();
        id.setPersister(manager);
        TestProviderController controller = new TestProviderController();
        controller.setIdentity(id);
        setController(controller);
        
    }
    void setTabLabels() {
        jTabbedPane1.setTitleAt(2, getResourceName("create_role"));
        
        jTabbedPane1.setTitleAt(1, getResourceName("create_provider"));
        jTabbedPane1.setTitleAt(0, getResourceName("find_provider"));
        
        
    }
    
    void setSexComboLabels() {
        DefaultComboBoxModel model = new DefaultComboBoxModel( new String[] { Globals.bundle.getString("male"), Globals.bundle.getString("female") } );
        jComboBox1.setModel(model);
        
    }
    
    String getResourceName(String key) {
        return  ResourceBundle.getBundle(BUNDLE).getString(key);
    }
    
    identity_role createRole( String name, identity_role[] directSuperclasses) {
        identity_role role = null;
        try {
            role = getController().createOrFindRole(name);
            if (role == null) {
                role = new identity_role();
                role.setName(name);
            }
        } catch (Exception e) {
            e.printStackTrace();
            role = new identity_role();
            role.setName(name);
        }
        
        if (directSuperclasses == null)
            return role;
        
        getController().getManagerReference().setConnected(true);
        
        for (int i = 0; i < directSuperclasses.length; ++i) {
            role.addSuperType(directSuperclasses[i]);
            
        }
        getController().getManagerReference().getIdentityManager().updateRole(role);
        getController().getManagerReference().setConnected(false);
        
        return role;
    }
    
    DefaultMutableTreeNode top ;
    identity_role[] supers ;
    DefaultMutableTreeNode specialists;
    DefaultMutableTreeNode gps ;
    identity_role[] specialistSuper ;
    DefaultMutableTreeNode obstetricians;
    DefaultMutableTreeNode surgeons;
    DefaultMutableTreeNode physicians ;
    DefaultMutableTreeNode psychs;
    identity_role[] surgeonSuper ;
    identity_role[] physicianSuper ;
    DefaultMutableTreeNode generalSurgeons ;
    DefaultMutableTreeNode generalPhysicians ;
    DefaultMutableTreeNode ent ;
    DefaultMutableTreeNode plastics;
    DefaultMutableTreeNode dermatologists;
    DefaultMutableTreeNode paediatricians ;
    DefaultMutableTreeNode paedsurgs ;
    DefaultMutableTreeNode cardiologist ;
    DefaultMutableTreeNode orthopods ;
    DefaultMutableTreeNode opthalmologists;
    DefaultMutableTreeNode urologists ;
    DefaultMutableTreeNode doctors;
    void postSetViewInit() {
        if (top != null)
            return;
        top = createNode("Providers"  , null );
        
        supers = new identity_role[] { (identity_role) top.getUserObject() };
        doctors = createNode("doctors", supers );
        identity_role[] doctorSuper = new identity_role[]  {(identity_role) doctors.getUserObject() };
        gps = createNode("gps", doctorSuper );
        specialists = createNode("specialists" , doctorSuper );
        specialistSuper = new identity_role[] { (identity_role) specialists.getUserObject() };
        obstetricians = createNode("obstetricians" , specialistSuper  );
        surgeons = createNode("surgeons" ,  specialistSuper );
        physicians = createNode("physicians" , specialistSuper );
        psychs = createNode("psychiatrists" , specialistSuper );
        
        surgeonSuper = new identity_role[] { (identity_role) surgeons.getUserObject() };
        physicianSuper = new identity_role[] { (identity_role) physicians.getUserObject() };
        generalSurgeons = createNode("general_surgeons" , surgeonSuper  );
        generalPhysicians = createNode("general_physicians" , physicianSuper  );
        ent = createNode("ent_surgeons" , surgeonSuper    );
        plastics = createNode("plastics" , surgeonSuper   );
        dermatologists = createNode("dermatologists" , physicianSuper  );
        paediatricians = createNode("paediatricians", physicianSuper  );
        paedsurgs = createNode("paediatric_surgeons", surgeonSuper  );
        cardiologist = createNode("cardiologists", physicianSuper );
        orthopods = createNode("orthopaedic_surgeons" , surgeonSuper  );
        urologists = createNode("urologists" , surgeonSuper);
        opthalmologists = createNode("opthalmologists" , surgeonSuper);
        
        try {
            createProviderModel();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    DefaultMutableTreeNode createNode( String resourceKey, identity_role[] superRoles) {
        return new DefaultMutableTreeNode( createRole(getResourceName(resourceKey), superRoles) );
    }
    
    void createProviderModel() {
        top.add(doctors);
        doctors.add(specialists);
        doctors.add(gps);
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
        surgeons.add(opthalmologists);
        surgeons.add(urologists);
        surgeons.add(paedsurgs);
        surgeons.add(plastics);
        jTree1.setModel(new DefaultTreeModel(top));
        jTree3.setModel( new DefaultTreeModel(top));
        findjTree2.setModel( new DefaultTreeModel( top ) );
        
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
        jMenuItem2 = new javax.swing.JMenuItem();
        buttonGroup1 = new javax.swing.ButtonGroup();
        findProviderByRolePopupMenu = new javax.swing.JPopupMenu();
        searchRoleMenuItem = new javax.swing.JMenuItem();
        clearRoleSekectMenuItem = new javax.swing.JMenuItem();
        jTabbedPane1 = new javax.swing.JTabbedPane();
        jPanel2 = new javax.swing.JPanel();
        jLabel2 = new javax.swing.JLabel();
        searchNamesjTextField2 = new javax.swing.JTextField();
        jLabel3 = new javax.swing.JLabel();
        locationjComboBox1 = new javax.swing.JComboBox();
        jScrollPane5 = new javax.swing.JScrollPane();
        findjTree2 = new javax.swing.JTree();
        jButton5 = new javax.swing.JButton();
        jScrollPane2 = new javax.swing.JScrollPane();
        resultjList1 = new javax.swing.JList();
        editButton = new javax.swing.JButton();
        jButton6 = new javax.swing.JButton();
        jPanel3 = new javax.swing.JPanel();
        jPanel5 = new javax.swing.JPanel();
        jLabel5 = new javax.swing.JLabel();
        lastNamesjTextField3 = new javax.swing.JTextField();
        jLabel6 = new javax.swing.JLabel();
        firstNamesjTextField4 = new javax.swing.JTextField();
        jPanel6 = new javax.swing.JPanel();
        jLabel4 = new javax.swing.JLabel();
        jComboBox1 = new javax.swing.JComboBox();
        jLabel9 = new javax.swing.JLabel();
        addressjTextField5 = new javax.swing.JTextField();
        jLabel10 = new javax.swing.JLabel();
        telephonejTextField6 = new javax.swing.JTextField();
        jLabel11 = new javax.swing.JLabel();
        faxjTextField7 = new javax.swing.JTextField();
        jLabel13 = new javax.swing.JLabel();
        mobilejTextField3 = new javax.swing.JTextField();
        jLabel14 = new javax.swing.JLabel();
        pagerjTextField4 = new javax.swing.JTextField();
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
        jButton3 = new javax.swing.JButton();
        deleteButton7 = new javax.swing.JButton();
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

        jMenuItem2.setText(java.util.ResourceBundle.getBundle("SummaryTerms").getString("clear_selection"));
        jMenuItem2.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                clearRoleTreeSelection(evt);
            }
        });

        jPopupMenu1.add(jMenuItem2);

        searchRoleMenuItem.setText(java.util.ResourceBundle.getBundle("SummaryTerms").getString("search_role"));
        searchRoleMenuItem.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                searchRoleMenuItemActionPerformed(evt);
            }
        });

        findProviderByRolePopupMenu.add(searchRoleMenuItem);

        clearRoleSekectMenuItem.setText(java.util.ResourceBundle.getBundle("SummaryTerms").getString("clear_selection"));
        clearRoleSekectMenuItem.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                clearRoleSekectMenuItemActionPerformed(evt);
            }
        });

        findProviderByRolePopupMenu.add(clearRoleSekectMenuItem);

        setLayout(new java.awt.BorderLayout());

        jPanel2.setLayout(new java.awt.GridBagLayout());

        jLabel2.setHorizontalAlignment(javax.swing.SwingConstants.TRAILING);
        jLabel2.setText(java.util.ResourceBundle.getBundle("SummaryTerms").getString("lastname_firstname"));
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        jPanel2.add(jLabel2, gridBagConstraints);

        searchNamesjTextField2.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                searchNamesjTextField2ActionPerformed(evt);
            }
        });

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        gridBagConstraints.weightx = 1.0;
        jPanel2.add(searchNamesjTextField2, gridBagConstraints);

        jLabel3.setHorizontalAlignment(javax.swing.SwingConstants.RIGHT);
        jLabel3.setText(java.util.ResourceBundle.getBundle("SummaryTerms").getString("location"));
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        jPanel2.add(jLabel3, gridBagConstraints);

        locationjComboBox1.setEditable(true);
        locationjComboBox1.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                locationjComboBox1ActionPerformed(evt);
            }
        });

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        jPanel2.add(locationjComboBox1, gridBagConstraints);

        findjTree2.setBorder(new javax.swing.border.TitledBorder(java.util.ResourceBundle.getBundle("SummaryTerms").getString("role")));
        findjTree2.setToggleClickCount(1);
        findjTree2.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyPressed(java.awt.event.KeyEvent evt) {
                findjTree2KeyPressed(evt);
            }
            public void keyTyped(java.awt.event.KeyEvent evt) {
                findTreeSelectionTransferAction(evt);
            }
        });
        findjTree2.addMouseListener(new java.awt.event.MouseAdapter() {
            public void mouseClicked(java.awt.event.MouseEvent evt) {
                findjTree2MouseClicked(evt);
            }
            public void mousePressed(java.awt.event.MouseEvent evt) {
                findByRoleMousePressed(evt);
            }
            public void mouseReleased(java.awt.event.MouseEvent evt) {
                findjTree2MouseReleased(evt);
            }
        });

        jScrollPane5.setViewportView(findjTree2);

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.fill = java.awt.GridBagConstraints.BOTH;
        jPanel2.add(jScrollPane5, gridBagConstraints);

        jButton5.setMnemonic(java.util.ResourceBundle.getBundle("SummaryTerms").getString("search").charAt(0));
        jButton5.setText(java.util.ResourceBundle.getBundle("SummaryTerms").getString("search"));
        jButton5.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                searchProviderActionPerformed(evt);
            }
        });

        jPanel2.add(jButton5, new java.awt.GridBagConstraints());

        resultjList1.setBorder(new javax.swing.border.TitledBorder(java.util.ResourceBundle.getBundle("SummaryTerms").getString("results")));
        resultjList1.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyPressed(java.awt.event.KeyEvent evt) {
                resultjList1KeyPressed(evt);
            }
        });

        jScrollPane2.setViewportView(resultjList1);

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        gridBagConstraints.fill = java.awt.GridBagConstraints.BOTH;
        gridBagConstraints.weightx = 1.0;
        gridBagConstraints.weighty = 1.0;
        jPanel2.add(jScrollPane2, gridBagConstraints);

        editButton.setMnemonic(java.util.ResourceBundle.getBundle("SummaryTerms").getString("edit_selected").charAt(0));
        editButton.setText(java.util.ResourceBundle.getBundle("SummaryTerms").getString("edit_selected"));
        editButton.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                editButtonActionPerformed(evt);
            }
        });

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.RELATIVE;
        gridBagConstraints.anchor = java.awt.GridBagConstraints.WEST;
        gridBagConstraints.weightx = 1.0;
        jPanel2.add(editButton, gridBagConstraints);

        jButton6.setText(java.util.ResourceBundle.getBundle("SummaryTerms").getString("set_current_user"));
        jButton6.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jButton6ActionPerformed(evt);
            }
        });

        jPanel2.add(jButton6, new java.awt.GridBagConstraints());

        jTabbedPane1.addTab("tab2", jPanel2);

        jPanel3.setLayout(new java.awt.GridBagLayout());

        jPanel5.setLayout(new java.awt.GridBagLayout());

        jLabel5.setText(java.util.ResourceBundle.getBundle("SummaryTerms").getString("last_names"));
        jPanel5.add(jLabel5, new java.awt.GridBagConstraints());

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        gridBagConstraints.weightx = 1.0;
        jPanel5.add(lastNamesjTextField3, gridBagConstraints);

        jLabel6.setText(java.util.ResourceBundle.getBundle("SummaryTerms").getString("firstnames"));
        jPanel5.add(jLabel6, new java.awt.GridBagConstraints());

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.RELATIVE;
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        gridBagConstraints.weightx = 1.0;
        jPanel5.add(firstNamesjTextField4, gridBagConstraints);

        jPanel6.setLayout(new java.awt.GridLayout(1, 0));

        jLabel4.setText(java.util.ResourceBundle.getBundle("SummaryTerms").getString("sex"));
        jPanel6.add(jLabel4);

        jPanel6.add(jComboBox1);

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        jPanel5.add(jPanel6, gridBagConstraints);

        jLabel9.setText(java.util.ResourceBundle.getBundle("SummaryTerms").getString("address"));
        jPanel5.add(jLabel9, new java.awt.GridBagConstraints());

        addressjTextField5.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                addressjTextField5ActionPerformed(evt);
            }
        });

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        jPanel5.add(addressjTextField5, gridBagConstraints);

        jLabel10.setText(java.util.ResourceBundle.getBundle("SummaryTerms").getString("telephone"));
        jPanel5.add(jLabel10, new java.awt.GridBagConstraints());

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        jPanel5.add(telephonejTextField6, gridBagConstraints);

        jLabel11.setText(java.util.ResourceBundle.getBundle("SummaryTerms").getString("fax"));
        jPanel5.add(jLabel11, new java.awt.GridBagConstraints());

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        gridBagConstraints.weightx = 1.0;
        jPanel5.add(faxjTextField7, gridBagConstraints);

        jLabel13.setText(java.util.ResourceBundle.getBundle("SummaryTerms").getString("mobile"));
        jPanel5.add(jLabel13, new java.awt.GridBagConstraints());

        mobilejTextField3.setText(" ");
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        gridBagConstraints.weightx = 1.0;
        jPanel5.add(mobilejTextField3, gridBagConstraints);

        jLabel14.setText(java.util.ResourceBundle.getBundle("SummaryTerms").getString("pager"));
        jPanel5.add(jLabel14, new java.awt.GridBagConstraints());

        pagerjTextField4.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                pagerjTextField4ActionPerformed(evt);
            }
        });

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        gridBagConstraints.weightx = 1.0;
        jPanel5.add(pagerjTextField4, gridBagConstraints);

        jLabel7.setText(java.util.ResourceBundle.getBundle("SummaryTerms").getString("comments"));
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
        jList2.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyPressed(java.awt.event.KeyEvent evt) {
                deleteFromListHandler(evt);
            }
        });

        jScrollPane3.setViewportView(jList2);

        jPanel4.add(jScrollPane3);

        jTree3.setToolTipText("shift left selects into the list, shift-right deletes from the list");
        jTree3.setToggleClickCount(1);
        jTree3.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyPressed(java.awt.event.KeyEvent evt) {
                jTree3KeyPressed(evt);
            }
        });
        jTree3.addMouseListener(new java.awt.event.MouseAdapter() {
            public void mouseClicked(java.awt.event.MouseEvent evt) {
                roleTreeClicked(evt);
            }
            public void mousePressed(java.awt.event.MouseEvent evt) {
                checkForPopup(evt);
            }
            public void mouseReleased(java.awt.event.MouseEvent evt) {
                jTree3MouseReleased(evt);
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

        jButton4.setText(java.util.ResourceBundle.getBundle("SummaryTerms").getString("save_provider"));
        jButton4.setToolTipText("add the providerwith the listed roles");
        jButton4.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                createProviderActionPerformed(evt);
            }
        });

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        jPanel3.add(jButton4, gridBagConstraints);

        jLabel8.setText(java.util.ResourceBundle.getBundle("SummaryTerms").getString("occupied_roles"));
        jPanel3.add(jLabel8, new java.awt.GridBagConstraints());

        jSeparator1.setOrientation(javax.swing.SwingConstants.VERTICAL);
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = 2;
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        gridBagConstraints.weightx = 1.0;
        jPanel3.add(jSeparator1, gridBagConstraints);

        jLabel12.setHorizontalAlignment(javax.swing.SwingConstants.RIGHT);
        jLabel12.setText(java.util.ResourceBundle.getBundle("SummaryTerms").getString("provider_tree_command"));
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        gridBagConstraints.anchor = java.awt.GridBagConstraints.EAST;
        jPanel3.add(jLabel12, gridBagConstraints);

        jButton3.setText(java.util.ResourceBundle.getBundle("SummaryTerms").getString("clear"));
        jButton3.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                clearIdentityActionPerformed(evt);
            }
        });

        jPanel3.add(jButton3, new java.awt.GridBagConstraints());

        deleteButton7.setText(java.util.ResourceBundle.getBundle("SummaryTerms").getString("delete"));
        deleteButton7.setEnabled(false);
        deleteButton7.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                deleteButton7ActionPerformed(evt);
            }
        });

        jPanel3.add(deleteButton7, new java.awt.GridBagConstraints());

        jTabbedPane1.addTab("tab3", jPanel3);

        jPanel1.setLayout(new java.awt.GridBagLayout());

        jLabel1.setText(java.util.ResourceBundle.getBundle("SummaryTerms").getString("role_name"));
        jPanel1.add(jLabel1, new java.awt.GridBagConstraints());

        jTextField1.setColumns(20);
        jTextField1.setText("jTextField1");
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        gridBagConstraints.weightx = 1.0;
        jPanel1.add(jTextField1, gridBagConstraints);

        jCheckBox1.setText(java.util.ResourceBundle.getBundle("SummaryTerms").getString("is_sub_role_of"));
        jCheckBox1.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jCheckBox1ActionPerformed(evt);
            }
        });

        jPanel1.add(jCheckBox1, new java.awt.GridBagConstraints());

        jTree1.setToggleClickCount(1);
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

        jButton1.setText(java.util.ResourceBundle.getBundle("SummaryTerms").getString("add_role_category"));
        jPanel1.add(jButton1, new java.awt.GridBagConstraints());

        jButton2.setText(java.util.ResourceBundle.getBundle("SummaryTerms").getString("remove_category"));
        jButton2.setToolTipText(java.util.ResourceBundle.getBundle("SummaryTerms").getString("remove_role_hint"));
        jPanel1.add(jButton2, new java.awt.GridBagConstraints());

        jTabbedPane1.addTab("tab1", jPanel1);

        add(jTabbedPane1, java.awt.BorderLayout.CENTER);

    }//GEN-END:initComponents
    
    private void deleteButton7ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_deleteButton7ActionPerformed
        // Add your handling code here:
        deleteProvider();
    }//GEN-LAST:event_deleteButton7ActionPerformed
    
    private void jButton6ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jButton6ActionPerformed
        // Add your handling code here:
        // temporary hack for script writing provider .
        int ix =  resultjList1.getSelectedIndex();
        if (ix >= 0)
            Globals.setUserIdentity( resultjList1.getSelectedValue() );
    }//GEN-LAST:event_jButton6ActionPerformed
    
    private void resultjList1KeyPressed(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_resultjList1KeyPressed
        // Add your handling code here:
        if (evt.getKeyCode() == evt.VK_ENTER) {
            setProviderSelected(true);
            setProviderSelected(false);
        }
        
    }//GEN-LAST:event_resultjList1KeyPressed
    
    private void searchNamesjTextField2ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_searchNamesjTextField2ActionPerformed
        // Add your handling code here:
        searchProviderActionPerformed(new java.awt.event.ActionEvent( evt.getSource(), 1, "search for providers with role"));
    }//GEN-LAST:event_searchNamesjTextField2ActionPerformed
    
    private void jTree3MouseReleased(java.awt.event.MouseEvent evt) {//GEN-FIRST:event_jTree3MouseReleased
        // Add your handling code here:
        checkForPopup(evt);
    }//GEN-LAST:event_jTree3MouseReleased
    
    private void findjTree2MouseReleased(java.awt.event.MouseEvent evt) {//GEN-FIRST:event_findjTree2MouseReleased
        // Add your handling code here:
        findByRoleMousePressed(evt);
    }//GEN-LAST:event_findjTree2MouseReleased
    
    private void findjTree2MouseClicked(java.awt.event.MouseEvent evt) {//GEN-FIRST:event_findjTree2MouseClicked
        // Add your handling code here:
        findByRoleMousePressed(evt);
    }//GEN-LAST:event_findjTree2MouseClicked
    
    private void findByRoleMousePressed(java.awt.event.MouseEvent evt) {//GEN-FIRST:event_findByRoleMousePressed
        // Add your handling code here:
        if (evt.isPopupTrigger()) {
            
            findProviderByRolePopupMenu.show((java.awt.Component)evt.getSource(), evt.getX(), evt.getY());
        }
    }//GEN-LAST:event_findByRoleMousePressed
    
    private void clearRoleSekectMenuItemActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_clearRoleSekectMenuItemActionPerformed
        // Add your handling code here:
        findjTree2.clearSelection();
    }//GEN-LAST:event_clearRoleSekectMenuItemActionPerformed
    
    private void searchRoleMenuItemActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_searchRoleMenuItemActionPerformed
        // Add your handling code here:
        searchProviderActionPerformed(new java.awt.event.ActionEvent( evt.getSource(), 1, "search for providers with role"));
    }//GEN-LAST:event_searchRoleMenuItemActionPerformed
    
    private void roleTreeClicked(java.awt.event.MouseEvent evt) {//GEN-FIRST:event_roleTreeClicked
        // Add your handling code here:
        if (evt.getClickCount() == 2)
            addSelectedRoleInTreeToList();
        checkForPopup(evt);
    }//GEN-LAST:event_roleTreeClicked
    
    private void clearRoleTreeSelection(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_clearRoleTreeSelection
        // Add your handling code here:
        //        findjTree2.clearSelection();
        jTree3.clearSelection();
    }//GEN-LAST:event_clearRoleTreeSelection
    
    private void findjTree2KeyPressed(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_findjTree2KeyPressed
        // Add your handling code here:
        if (evt.getKeyCode() == evt.VK_ENTER) {
            
            searchProviderActionPerformed(new java.awt.event.ActionEvent( evt.getSource(), evt.VK_ENTER, "search for providers with role"));
        }
    }//GEN-LAST:event_findjTree2KeyPressed
    
    private void findTreeSelectionTransferAction(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_findTreeSelectionTransferAction
        // Add your handling code here:
        
    }//GEN-LAST:event_findTreeSelectionTransferAction
    
    private void clearIdentityActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_clearIdentityActionPerformed
        // Add your handling code here:
        
        getController().setProvider(new identity());
    }//GEN-LAST:event_clearIdentityActionPerformed
    
    private void deleteFromListHandler(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_deleteFromListHandler
        // Add your handling code here:
        if (evt.getKeyCode() == evt.VK_DELETE) {
            Object[] oo = jList2.getSelectedValues();
            for (int i = 0; i < oo.length; ++i) {
                addRemoved(oo[i]);
            }
        }
    }//GEN-LAST:event_deleteFromListHandler
    
    private void editButtonActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_editButtonActionPerformed
        // Add your handling code here:
        Object o = resultjList1.getSelectedValue();
        if ( o instanceof identity) {
            getController().setProvider( (identity ) o);
            getController().modelToUi();
            
            jTabbedPane1.setSelectedIndex(1);
            
            checkDeleteButtonState();
        }
    }//GEN-LAST:event_editButtonActionPerformed
    
    private void searchProviderActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_searchProviderActionPerformed
        // Add your handling code here:
        searchAction();
        
    }
    
    void searchAction() {
        String[] names = searchNamesjTextField2.getText().trim().split(",");
        String lastName = names[0].trim();
        
        String firstName = names.length > 1 ? names[1].trim() : "";
        TreePath [] paths = findjTree2.getSelectionPaths();
        List roles = new ArrayList();
        
        for (int i = 0; paths != null && i < paths.length; ++i) {
            Object o =  paths[i].getLastPathComponent();
            addLeafRoles(roles, (TreeNode) o);
        }
        try {
            //            resultjList1.setListData( new Object[0]);
            
            List l =  getController().getManagerReference().getIdentityManager().findProviders( lastName, firstName, (identity_role[])roles.toArray( new identity_role[0] ));
            
            resultjList1.setListData(l.toArray());
        } catch (Exception e) {
            e.printStackTrace();
        }
    }//GEN-LAST:event_searchProviderActionPerformed
    void addLeafRoles(List roles, TreeNode node) {
        
        if   ( node instanceof DefaultMutableTreeNode)  {
            DefaultMutableTreeNode dnode = (DefaultMutableTreeNode) node;
            if ( dnode.getUserObject() instanceof identity_role)
                roles.add( dnode.getUserObject());
        }
        
        if (node.isLeaf())
            return;
        for (int i = 0; i < node.getChildCount() ; ++i)
            addLeafRoles(roles, node.getChildAt(i));
        
    }
    
    private void locationjComboBox1ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_locationjComboBox1ActionPerformed
        // Add your handling code here:
    }//GEN-LAST:event_locationjComboBox1ActionPerformed
    
    private void createProviderActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_createProviderActionPerformed
        // Add your handling code here:
        getController().uiToModel();
        getController().save();
        
        getController().getManagerReference().getIdentityManager()
        .removeRoles(getController().getProvider(), getRemoved());
        clearRemoved();
        checkDeleteButtonState();
    }//GEN-LAST:event_createProviderActionPerformed
    
    private void pagerjTextField4ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_pagerjTextField4ActionPerformed
        // Add your handling code here:
    }//GEN-LAST:event_pagerjTextField4ActionPerformed
    
    private void addressjTextField5ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_addressjTextField5ActionPerformed
        // Add your handling code here:
    }//GEN-LAST:event_addressjTextField5ActionPerformed
    
    private void jTree3KeyPressed(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_jTree3KeyPressed
        // Add your handling code here:
        
        if ( evt.getKeyCode() == evt.VK_LEFT && ( evt.getModifiersEx() & evt.CTRL_DOWN_MASK ) != 0  )
            addSelectedRoleInTreeToList();
        else
            if (evt.getKeyCode() == evt.VK_RIGHT && ( evt.getModifiersEx() & evt.CTRL_DOWN_MASK) != 0  )
                deleteSelectedRoleInTreeFromList();
        
    }//GEN-LAST:event_jTree3KeyPressed
    
    private void checkForPopup(java.awt.event.MouseEvent evt) {//GEN-FIRST:event_checkForPopup
        // Add your handling code here:
        if (evt.isPopupTrigger()) {
            
            jPopupMenu1.show((java.awt.Component)evt.getSource(), evt.getX(), evt.getY());
        }
    }//GEN-LAST:event_checkForPopup
    
    private void jCheckBox1ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jCheckBox1ActionPerformed
        // Add your handling code here:
    }//GEN-LAST:event_jCheckBox1ActionPerformed
    
    
    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JTextField addressjTextField5;
    private javax.swing.ButtonGroup buttonGroup1;
    private javax.swing.JMenuItem clearRoleSekectMenuItem;
    private javax.swing.JTextArea commentText;
    private javax.swing.JButton deleteButton7;
    private javax.swing.JButton editButton;
    private javax.swing.JTextField faxjTextField7;
    private javax.swing.JPopupMenu findProviderByRolePopupMenu;
    private javax.swing.JTree findjTree2;
    private javax.swing.JTextField firstNamesjTextField4;
    private javax.swing.JButton jButton1;
    private javax.swing.JButton jButton2;
    private javax.swing.JButton jButton3;
    private javax.swing.JButton jButton4;
    private javax.swing.JButton jButton5;
    private javax.swing.JButton jButton6;
    private javax.swing.JCheckBox jCheckBox1;
    private javax.swing.JComboBox jComboBox1;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel10;
    private javax.swing.JLabel jLabel11;
    private javax.swing.JLabel jLabel12;
    private javax.swing.JLabel jLabel13;
    private javax.swing.JLabel jLabel14;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JLabel jLabel3;
    private javax.swing.JLabel jLabel4;
    private javax.swing.JLabel jLabel5;
    private javax.swing.JLabel jLabel6;
    private javax.swing.JLabel jLabel7;
    private javax.swing.JLabel jLabel8;
    private javax.swing.JLabel jLabel9;
    private javax.swing.JList jList2;
    private javax.swing.JMenuItem jMenuItem1;
    private javax.swing.JMenuItem jMenuItem2;
    private javax.swing.JPanel jPanel1;
    private javax.swing.JPanel jPanel2;
    private javax.swing.JPanel jPanel3;
    private javax.swing.JPanel jPanel4;
    private javax.swing.JPanel jPanel5;
    private javax.swing.JPanel jPanel6;
    private javax.swing.JPopupMenu jPopupMenu1;
    private javax.swing.JScrollPane jScrollPane1;
    private javax.swing.JScrollPane jScrollPane2;
    private javax.swing.JScrollPane jScrollPane3;
    private javax.swing.JScrollPane jScrollPane4;
    private javax.swing.JScrollPane jScrollPane5;
    private javax.swing.JSeparator jSeparator1;
    private javax.swing.JTabbedPane jTabbedPane1;
    private javax.swing.JTextField jTextField1;
    private javax.swing.JTree jTree1;
    private javax.swing.JTree jTree3;
    private javax.swing.JTextField lastNamesjTextField3;
    private javax.swing.JComboBox locationjComboBox1;
    private javax.swing.JTextField mobilejTextField3;
    private javax.swing.JTextField pagerjTextField4;
    private javax.swing.JList resultjList1;
    private javax.swing.JTextField searchNamesjTextField2;
    private javax.swing.JMenuItem searchRoleMenuItem;
    private javax.swing.JTextField telephonejTextField6;
    // End of variables declaration//GEN-END:variables
    
    /** Holds value of property providerSelected. */
    private boolean providerSelected;
    
    /** Utility field used by bound properties. */
    private java.beans.PropertyChangeSupport propertyChangeSupport =  new java.beans.PropertyChangeSupport(this);
    
    /** Holds value of property selectedUser. */
    private identity selectedUser;
    
    //    static Class[] roleFilter = { identity_role.class };
    
    
    
    public Collection getRemoved() {
        return removed;
    }
    
    public void  clearRemoved() {
        removed.clear();
    }
    
    public void addRemoved(Object o) {
        removed.add(o);
        getController().getProvider().getRoles().remove(o);
        ((DefaultListModel)jList2.getModel()).removeElement(o);
    }
    
    static interface DefaultListModelOperation {
        public void doOperation( DefaultListModel model, Object arg);
    }
    
    static class AddRoleInfoToListOperation implements DefaultListModelOperation {
        public void doOperation( DefaultListModel model, Object arg) {
            if (! ( arg instanceof identity_role))
                return;
            identity_role_info info = new identity_role_info();
            info.setComments("none");
            info.setIdentity_role((identity_role)arg);
            model.addElement(info);
        }
    }
    
    class RemoveRoleInfoFromListOperation implements DefaultListModelOperation {
        
        public void doOperation(DefaultListModel model, Object arg) {
            for ( int i =0; i < model.getSize(); ++i) {
                if ( ! (model.getElementAt(i) instanceof identity_role_info) )
                    continue;
                
                identity_role_info info = (identity_role_info) model.getElementAt(i);
                if ( !info.getIdentity_role().equals( arg) )
                    continue;
                addRemoved(info);
                
                return;
            }
        }
    }
    
    
    
    void addSelectedRoleInTreeToList() {
        Logger.global.info("  ** ");
        templateTreeToListAction(jTree3, jList2, new ContactsPanel.AddRoleInfoToListOperation() );
    }
    
    void deleteSelectedRoleInTreeFromList() {
        Logger.global.info("  ** ");
        templateTreeToListAction(jTree3, jList2, new ContactsPanel.RemoveRoleInfoFromListOperation() );
    }
    
    void templateTreeToListAction( JTree tree, JList list, ContactsPanel.DefaultListModelOperation op) {
        TreePath[] paths = tree.getSelectionPaths();
        for (int i =0; i < paths.length; ++i) {
            if ( paths[i].getLastPathComponent() instanceof DefaultMutableTreeNode) {
                DefaultMutableTreeNode node = (DefaultMutableTreeNode) paths[i].getLastPathComponent();
                if (node.getUserObject() == null)
                    continue;
                
                DefaultListModel model = (DefaultListModel) list.getModel();
                op.doOperation(model,  node.getUserObject());
                
            }
        }
        
    }
    
    public String getAddress() {
        return addressjTextField5.getText().trim();
    }
    
    public String getFax() {
        return faxjTextField7.getText().trim();
    }
    
    public String getFirstNames() {
        
        return firstNamesjTextField4.getText().trim();
    }
    
    
    public Collection getIdentity_role_info() {
        DefaultListModel model = (DefaultListModel )jList2.getModel();
        Logger.global.fine("model data = " + model.toArray());
        return Arrays.asList(model.toArray());
    }
    
    public String getLastNames() {
        return lastNamesjTextField3.getText().trim();
    }
    
    public String getMobile() {
        return mobilejTextField3.getText().trim();
    }
    
    public String getPager() {
        return mobilejTextField3.getText().trim();
    }
    
    public String getTelephone() {
        return telephonejTextField6.getText().trim();
    }
    
    public void setAddress(String address) {
        addressjTextField5.setText(address);
    }
    
    public void setFax(String fax) {
        faxjTextField7.setText(fax);
    }
    
    public void setFirstNames(String firstNames) {
        firstNamesjTextField4.setText(firstNames);
    }
    
    public void setIdentity_role_info(Collection identity_role_info) {
        DefaultListModel model = new DefaultListModel();
        for ( Iterator j = identity_role_info.iterator(); j .hasNext() ; model.addElement(j.next()) );
        jList2.setModel(model);
    }
    
    public void setLastNames(String lastNames) {
        lastNamesjTextField3.setText(lastNames);
    }
    
    public void setMobile(String mobile) {
        mobilejTextField3.setText(mobile);
    }
    
    public void setPager(String pager) {
        pagerjTextField4.setText(pager);
        
    }
    
    public void setTelephone(String telephone) {
        telephonejTextField6.setText(telephone);
    }
    
    /** Getter for property controller.
     * @return Value of property controller.
     *
     */
    public ProviderController getController() {
        return controller;
    }
    
    /** Setter for property controller.
     * @param controller New value of property controller.
     *
     */
    public void setController(ProviderController controller) {
        this.controller = controller;
        controller.setView(this);
        postSetViewInit();
    }
    
    public String getSex() {
        return (String) jComboBox1.getSelectedItem();
    }
    
    public void setSex(String sex) {
        jComboBox1.setEditable(true);
        jComboBox1.setSelectedItem(sex);
        jComboBox1.setEditable(false);
    }
    
    /** Getter for property selectedProvider.
     * @return Value of property selectedProvider.
     *
     */
    public identity getSelectedProvider() {
        Object o = resultjList1.getSelectedValue();
        if (o != null && o instanceof identity) {
            return (identity) o;
        }
        return null;
    }
    
    /** Adds a PropertyChangeListener to the listener list.
     * @param l The listener to add.
     *
     */
    public void addPropertyChangeListener(java.beans.PropertyChangeListener l) {
        propertyChangeSupport.addPropertyChangeListener(l);
    }
    
    /** Removes a PropertyChangeListener from the listener list.
     * @param l The listener to remove.
     *
     */
    public void removePropertyChangeListener(java.beans.PropertyChangeListener l) {
        propertyChangeSupport.removePropertyChangeListener(l);
    }
    
    /** Getter for property providerSelected.
     * @return Value of property providerSelected.
     *
     */
    public boolean isProviderSelected() {
        return this.providerSelected;
    }
    
    /** Setter for property providerSelected.
     * @param providerSelected New value of property providerSelected.
     *
     */
    public void setProviderSelected(boolean providerSelected) {
        boolean oldProviderSelected = this.providerSelected;
        this.providerSelected = providerSelected;
        propertyChangeSupport.firePropertyChange("providerSelected", new Boolean(oldProviderSelected), new Boolean(providerSelected));
        
    }
    
    /** Getter for property selectedUser.
     * @return Value of property selectedUser.
     *
     */
    public identity getSelectedUser() {
        return this.selectedUser;
    }
    
    /** Setter for property selectedUser.
     * @param selectedUser New value of property selectedUser.
     *
     */
    public void setSelectedUser(identity selectedUser) {
        this.selectedUser = selectedUser;
        
        
    }
    
    public boolean isSaved() {
        return getController().isSaved();
    }
    
    
    void confirm(String msg) throws RuntimeException {
        if ( JOptionPane.showConfirmDialog(JOptionPane.getDesktopPaneForComponent(this), msg) == JOptionPane.YES_OPTION)
            return;
        throw new RuntimeException(Globals.bundle.getString("operation_cancelled"));
        
    }
    
    void deleteProvider() {
        confirm(Globals.bundle.getString("confirm_delete"));
        getController().delete();
        searchAction();
        checkDeleteButtonState();
    }
    
    void checkDeleteButtonState() {
        deleteButton7.setEnabled(isSaved());
    }
}
