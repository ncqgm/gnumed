/*
 * OtherSummaryPanel.java
 *
 * Created on 03 April 2003, 17:51
 */

package quickmed.usecases.test;
import javax.swing.*;
import javax.swing.table.*;
import javax.swing.event.*;
import java.util.*;
import java.util.logging.*;
import java.awt.*;

import org.gnumed.gmIdentity.*;
/**
 *
 * @author  sjtan
 */
public class OtherSummaryPanel extends javax.swing.JPanel {
    public static final int DATE_WIDTH=70;
    public static final int PREF_PROBLEM_WIDTH=300;
    public static final int NO_WIDTH=30;
    public static final int MAX_DIFF=100;
    public static final int DRUG_WIDTH = 200;
    public static final int DIRECTIONS_WIDTH = 200;
    
    ListObjectTableModel drugModel, problemModel;
    PrescribeDialog dialog ;
    Ref idRef = new Ref() {
        public Object getRef() {
            return getIdentity();
        }
    };
    
    /** Creates new form OtherSummaryPanel */
    public OtherSummaryPanel() {
        initComponents();
        createDrugTableModel();
        createProblemTableModel();
        resizeManagementColumns();
        resizeProblemColumns();
        resizeDrugColumns();
    }
    
    void createDrugTableModel() {
        ListObjectTableModel model = new ListObjectTableModel();
        DummyDrugViewFactory factory = new DummyDrugViewFactory();
        factory.setIdentityRef( idRef );
        model.setFactory(factory);
        model.newObject();
        drugModel = model;
        
        tableWithPopup1.setModel(model);
        model.loadDefaultEditors(tableWithPopup1.getTable().getColumnModel());
        
        //DefaultRenderer DOESN'T SEEM TO WORK THE WAY I THINK IT SHOOULD
        tableWithPopup1.getTable().setDefaultRenderer(java.util.Date.class, new ShortDateCellRenderer());
        //        OtherSummaryPanel.LinkDrugDialogCellEditorListener l = new OtherSummaryPanel.LinkDrugDialogCellEditorListener();
        
        SelectionDialogListObjectTableModelLinker l2 = new SelectionDialogListObjectTableModelLinker();
        l2.setTable( tableWithPopup1.getTable());
        l2.setDialog( new PrescribeDialog((Frame) SwingUtilities.getAncestorOfClass(Frame.class,
        OtherSummaryPanel.this), true ) );
        l2.setDialogColumn("drug");
    }
    
    void createProblemTableModel() {
        ListObjectTableModel model = new ListObjectTableModel();
        TestProblemViewFactory factory = new TestProblemViewFactory();
        factory.setIdRef(idRef);
        model.setFactory(factory);
        model.newObject();
        tableWithPopup2.setModel(model);
        model.loadDefaultEditors(tableWithPopup2.getTable().getColumnModel());
        SelectionDialogListObjectTableModelLinker l2 = new SelectionDialogListObjectTableModelLinker();
        l2.setTable( tableWithPopup2.getTable());
        l2.setDialog( new ProblemDialog((Frame) SwingUtilities.getAncestorOfClass(Frame.class,
        OtherSummaryPanel.this), true ) );
        l2.setDialogColumn("significantProblem");
        problemModel = model;
    }
    //    javax.swing.table.TableColumn getDrugTableColumn( String name) {
    //        ListObjectTableModel model = (ListObjectTableModel) tableWithPopup1.getModel();
    //        return tableWithPopup1.getTable().getColumnModel().getColumn(model.getColumnByName(name));
    //    }
    //
    protected void resizeProblemColumns() {
        tableWithPopup2.getTable().getColumnModel().getColumn(0).setPreferredWidth(DATE_WIDTH);
        tableWithPopup2.getTable().getColumnModel().getColumn(1).setPreferredWidth(PREF_PROBLEM_WIDTH);
        tableWithPopup2.getTable().getColumnModel().getColumn(0).setMaxWidth(DATE_WIDTH*2);
             tableWithPopup2.getTable().getColumnModel().getColumn(0).setMinWidth(DATE_WIDTH /4);
        tableWithPopup2.getTable().getColumnModel().getColumn(1).setMaxWidth(PREF_PROBLEM_WIDTH +MAX_DIFF/3);
        
    }
    protected void resizeDrugColumns() {
        tableWithPopup1.getTable().getColumnModel().getColumn(0).setPreferredWidth(DATE_WIDTH);
        tableWithPopup1.getTable().getColumnModel().getColumn(0).setMaxWidth(DATE_WIDTH + NO_WIDTH);
        
        tableWithPopup1.getTable().getColumnModel().getColumn(1).setPreferredWidth(DRUG_WIDTH);
        tableWithPopup1.getTable().getColumnModel().getColumn(1).setMaxWidth(DRUG_WIDTH + MAX_DIFF);
        
        tableWithPopup1.getTable().getColumnModel().getColumn(2).setPreferredWidth(DIRECTIONS_WIDTH );
        tableWithPopup1.getTable().getColumnModel().getColumn(2).setMaxWidth(DIRECTIONS_WIDTH + MAX_DIFF);
        
        
        
    }
    protected void resizeManagementColumns() {
        jTable4.getColumnModel().getColumn(0).setPreferredWidth(DATE_WIDTH);
        jTable4.getColumnModel().getColumn(2).setPreferredWidth(DATE_WIDTH);
        jTable4.getColumnModel().getColumn(0).setMaxWidth(DATE_WIDTH + MAX_DIFF);
        jTable4.getColumnModel().getColumn(2).setMaxWidth(DATE_WIDTH + MAX_DIFF);
        
    }
    
    /** This method is called from within the constructor to
     * initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is
     * always regenerated by the Form Editor.
     */
    private void initComponents() {//GEN-BEGIN:initComponents
        java.awt.GridBagConstraints gridBagConstraints;

        jSplitPane3 = new javax.swing.JSplitPane();
        jPanel6 = new javax.swing.JPanel();
        jPanel1 = new javax.swing.JPanel();
        jScrollPane6 = new javax.swing.JScrollPane();
        jTextArea1 = new javax.swing.JTextArea();
        jPanel2 = new javax.swing.JPanel();
        jLabel1 = new javax.swing.JLabel();
        jScrollPane7 = new javax.swing.JScrollPane();
        jTextArea2 = new javax.swing.JTextArea();
        jLabel2 = new javax.swing.JLabel();
        jScrollPane8 = new javax.swing.JScrollPane();
        jTextArea3 = new javax.swing.JTextArea();
        jLabel3 = new javax.swing.JLabel();
        jScrollPane9 = new javax.swing.JScrollPane();
        jTextArea4 = new javax.swing.JTextArea();
        jSplitPane1 = new javax.swing.JSplitPane();
        jPanel4 = new javax.swing.JPanel();
        jScrollPane1 = new javax.swing.JScrollPane();
        tableWithPopup2 = new quickmed.usecases.test.TableWithPopup();
        jScrollPane3 = new javax.swing.JScrollPane();
        jTable3 = new javax.swing.JTable();
        jScrollPane2 = new javax.swing.JScrollPane();
        jTable2 = new javax.swing.JTable();
        jPanel5 = new javax.swing.JPanel();
        jSplitPane2 = new javax.swing.JSplitPane();
        jScrollPane4 = new javax.swing.JScrollPane();
        jTable4 = new javax.swing.JTable();
        tableWithPopup1 = new quickmed.usecases.test.TableWithPopup();
        jPanel3 = new javax.swing.JPanel();
        jLabel4 = new javax.swing.JLabel();
        jTextField1 = new javax.swing.JTextField();
        jLabel5 = new javax.swing.JLabel();
        jTextField2 = new javax.swing.JTextField();
        jLabel6 = new javax.swing.JLabel();
        jTextField3 = new javax.swing.JTextField();
        jLabel7 = new javax.swing.JLabel();
        jTextField4 = new javax.swing.JTextField();
        jLabel8 = new javax.swing.JLabel();
        jTextField5 = new javax.swing.JTextField();
        jScrollPane5 = new javax.swing.JScrollPane();
        jTable5 = new javax.swing.JTable();

        setLayout(new java.awt.GridBagLayout());

        setMaximumSize(new java.awt.Dimension(1300, 800));
        setPreferredSize(new java.awt.Dimension(940, 426));
        jSplitPane3.setOrientation(javax.swing.JSplitPane.VERTICAL_SPLIT);
        jSplitPane3.setResizeWeight(0.2);
        jPanel6.setLayout(new java.awt.GridLayout(1, 0));

        jPanel1.setLayout(new java.awt.BorderLayout());

        jPanel1.setBorder(new javax.swing.border.TitledBorder(java.util.ResourceBundle.getBundle("SummaryTerms").getString("social_family_label")));
        jTextArea1.setLineWrap(true);
        jTextArea1.setWrapStyleWord(true);
        jScrollPane6.setViewportView(jTextArea1);

        jPanel1.add(jScrollPane6, java.awt.BorderLayout.CENTER);

        jPanel6.add(jPanel1);

        jPanel2.setLayout(new java.awt.GridBagLayout());

        jLabel1.setFont(new java.awt.Font("Dialog", 1, 10));
        jLabel1.setText(java.util.ResourceBundle.getBundle("SummaryTerms").getString("mother"));
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.fill = java.awt.GridBagConstraints.BOTH;
        gridBagConstraints.ipadx = 2;
        gridBagConstraints.anchor = java.awt.GridBagConstraints.NORTH;
        gridBagConstraints.weightx = 0.5;
        gridBagConstraints.weighty = 1.0;
        jPanel2.add(jLabel1, gridBagConstraints);

        jTextArea2.setLineWrap(true);
        jTextArea2.setWrapStyleWord(true);
        jScrollPane7.setViewportView(jTextArea2);

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        gridBagConstraints.fill = java.awt.GridBagConstraints.BOTH;
        jPanel2.add(jScrollPane7, gridBagConstraints);

        jLabel2.setFont(new java.awt.Font("Dialog", 1, 10));
        jLabel2.setText("Father");
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.fill = java.awt.GridBagConstraints.BOTH;
        gridBagConstraints.anchor = java.awt.GridBagConstraints.EAST;
        gridBagConstraints.weightx = 0.5;
        gridBagConstraints.weighty = 1.0;
        jPanel2.add(jLabel2, gridBagConstraints);

        jTextArea3.setLineWrap(true);
        jTextArea3.setWrapStyleWord(true);
        jScrollPane8.setViewportView(jTextArea3);

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        gridBagConstraints.fill = java.awt.GridBagConstraints.BOTH;
        gridBagConstraints.weightx = 1.0;
        jPanel2.add(jScrollPane8, gridBagConstraints);

        jLabel3.setFont(new java.awt.Font("Dialog", 1, 10));
        jLabel3.setText("Siblings/other");
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.fill = java.awt.GridBagConstraints.BOTH;
        gridBagConstraints.anchor = java.awt.GridBagConstraints.SOUTH;
        gridBagConstraints.weightx = 0.5;
        gridBagConstraints.weighty = 1.0;
        jPanel2.add(jLabel3, gridBagConstraints);

        jTextArea4.setLineWrap(true);
        jTextArea4.setWrapStyleWord(true);
        jScrollPane9.setViewportView(jTextArea4);

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        gridBagConstraints.fill = java.awt.GridBagConstraints.BOTH;
        gridBagConstraints.weightx = 1.0;
        jPanel2.add(jScrollPane9, gridBagConstraints);

        jPanel6.add(jPanel2);

        jSplitPane3.setLeftComponent(jPanel6);

        jSplitPane1.setOrientation(javax.swing.JSplitPane.VERTICAL_SPLIT);
        jSplitPane1.setResizeWeight(0.4);
        jPanel4.setLayout(new java.awt.GridBagLayout());

        jScrollPane1.setBorder(new javax.swing.border.TitledBorder(null, "Significant problems - past and present", javax.swing.border.TitledBorder.DEFAULT_JUSTIFICATION, javax.swing.border.TitledBorder.DEFAULT_POSITION, new java.awt.Font("Dialog", 1, 10)));
        jScrollPane1.setViewportView(tableWithPopup2);

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = 2;
        gridBagConstraints.gridheight = java.awt.GridBagConstraints.RELATIVE;
        gridBagConstraints.fill = java.awt.GridBagConstraints.BOTH;
        gridBagConstraints.weightx = 2.0;
        jPanel4.add(jScrollPane1, gridBagConstraints);

        jScrollPane3.setBorder(new javax.swing.border.TitledBorder("Immunizations"));
        jTable3.setModel(new javax.swing.table.DefaultTableModel(
            new Object [][] {
                {null, null, null},
                {null, null, null},
                {null, null, null},
                {null, null, null}
            },
            new String [] {
                "Date", "Type", "Batch"
            }
        ));
        jScrollPane3.setViewportView(jTable3);

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.RELATIVE;
        gridBagConstraints.gridheight = java.awt.GridBagConstraints.RELATIVE;
        gridBagConstraints.fill = java.awt.GridBagConstraints.BOTH;
        gridBagConstraints.weightx = 1.0;
        gridBagConstraints.weighty = 1.0;
        jPanel4.add(jScrollPane3, gridBagConstraints);

        jScrollPane2.setBorder(new javax.swing.border.TitledBorder("Allergies"));
        jTable2.setModel(new javax.swing.table.DefaultTableModel(
            new Object [][] {
                {null, null, null},
                {null, null, null},
                {null, null, null},
                {null, null, null}
            },
            new String [] {
                "Allergy", "Caution", "Severity"
            }
        ));
        jScrollPane2.setViewportView(jTable2);

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        gridBagConstraints.gridheight = java.awt.GridBagConstraints.RELATIVE;
        gridBagConstraints.fill = java.awt.GridBagConstraints.BOTH;
        gridBagConstraints.weightx = 1.0;
        gridBagConstraints.weighty = 0.5;
        jPanel4.add(jScrollPane2, gridBagConstraints);

        jSplitPane1.setLeftComponent(jPanel4);

        jPanel5.setLayout(new java.awt.BorderLayout());

        jSplitPane2.setResizeWeight(0.4);
        jSplitPane2.setOneTouchExpandable(true);
        jScrollPane4.setBorder(new javax.swing.border.TitledBorder("Management"));
        jTable4.setFont(new java.awt.Font("Dialog", 0, 10));
        jTable4.setModel(new javax.swing.table.DefaultTableModel(
            new Object [][] {
                {null, null, null},
                {null, null, null},
                {null, null, null},
                {null, null, null}
            },
            new String [] {
                "Date", "management", "ended"
            }
        ));
        jScrollPane4.setViewportView(jTable4);

        jSplitPane2.setLeftComponent(jScrollPane4);

        tableWithPopup1.setBorder(new javax.swing.border.TitledBorder(java.util.ResourceBundle.getBundle("SummaryTerms").getString("current_medication")));
        jSplitPane2.setRightComponent(tableWithPopup1);

        jPanel5.add(jSplitPane2, java.awt.BorderLayout.CENTER);

        jSplitPane1.setRightComponent(jPanel5);

        jSplitPane3.setRightComponent(jSplitPane1);

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridheight = 2;
        gridBagConstraints.fill = java.awt.GridBagConstraints.BOTH;
        gridBagConstraints.weightx = 20.0;
        gridBagConstraints.weighty = 1.0;
        add(jSplitPane3, gridBagConstraints);

        jPanel3.setLayout(new java.awt.GridBagLayout());

        jLabel4.setFont(new java.awt.Font("Dialog", 1, 10));
        jLabel4.setText("Alcohol");
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.anchor = java.awt.GridBagConstraints.WEST;
        gridBagConstraints.weightx = 1.0;
        jPanel3.add(jLabel4, gridBagConstraints);

        jTextField1.setColumns(2);
        jTextField1.setText("jTextField1");
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        gridBagConstraints.weightx = 5.0;
        gridBagConstraints.weighty = 1.0;
        jPanel3.add(jTextField1, gridBagConstraints);

        jLabel5.setFont(new java.awt.Font("Dialog", 1, 10));
        jLabel5.setText("Tobacco");
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.anchor = java.awt.GridBagConstraints.WEST;
        jPanel3.add(jLabel5, gridBagConstraints);

        jTextField2.setText("jTextField2");
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        gridBagConstraints.ipadx = 50;
        gridBagConstraints.weightx = 5.0;
        gridBagConstraints.weighty = 1.0;
        jPanel3.add(jTextField2, gridBagConstraints);

        jLabel6.setFont(new java.awt.Font("Dialog", 1, 10));
        jLabel6.setText("Physical Activity");
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.anchor = java.awt.GridBagConstraints.WEST;
        jPanel3.add(jLabel6, gridBagConstraints);

        jTextField3.setText("jTextField3");
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        gridBagConstraints.weightx = 5.0;
        gridBagConstraints.weighty = 1.0;
        jPanel3.add(jTextField3, gridBagConstraints);

        jLabel7.setFont(new java.awt.Font("Dialog", 1, 10));
        jLabel7.setText("Nutrition");
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.anchor = java.awt.GridBagConstraints.WEST;
        jPanel3.add(jLabel7, gridBagConstraints);

        jTextField4.setText("jTextField4");
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        gridBagConstraints.weightx = 5.0;
        gridBagConstraints.weighty = 1.0;
        jPanel3.add(jTextField4, gridBagConstraints);

        jLabel8.setFont(new java.awt.Font("Dialog", 1, 10));
        jLabel8.setText("Other");
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.anchor = java.awt.GridBagConstraints.WEST;
        jPanel3.add(jLabel8, gridBagConstraints);

        jTextField5.setText("jTextField5");
        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.fill = java.awt.GridBagConstraints.HORIZONTAL;
        gridBagConstraints.weightx = 5.0;
        gridBagConstraints.weighty = 1.0;
        jPanel3.add(jTextField5, gridBagConstraints);

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        gridBagConstraints.fill = java.awt.GridBagConstraints.BOTH;
        gridBagConstraints.weightx = 1.0;
        add(jPanel3, gridBagConstraints);

        jTable5.setFont(new java.awt.Font("Dialog", 0, 10));
        jTable5.setModel(new javax.swing.table.DefaultTableModel(
            new Object [][] {
                {"Height", null},
                {"Weight", null},
                {"BMI", null},
                {"BP", null},
                {"Tetanus", null},
                {"Influenza", null},
                {"Hepatitis", null},
                {"Sexuality", null},
                {"Cholesterol", null},
                {"Triglycerides", null},
                {"HDL", null},
                {"BSL", null},
                {"Cancer", null},
                {"Skin", null},
                {"Colorectal", null},
                {"Mammogram", null},
                {"Pap", null},
                {"HIV", null},
                {null, null}
            },
            new String [] {
                "Item", "screened"
            }
        ) {
            boolean[] canEdit = new boolean [] {
                false, true
            };

            public boolean isCellEditable(int rowIndex, int columnIndex) {
                return canEdit [columnIndex];
            }
        });
        jTable5.setAutoResizeMode(javax.swing.JTable.AUTO_RESIZE_NEXT_COLUMN);
        jTable5.setEditingColumn(1);
        jScrollPane5.setViewportView(jTable5);

        gridBagConstraints = new java.awt.GridBagConstraints();
        gridBagConstraints.gridwidth = java.awt.GridBagConstraints.REMAINDER;
        gridBagConstraints.gridheight = java.awt.GridBagConstraints.RELATIVE;
        gridBagConstraints.fill = java.awt.GridBagConstraints.BOTH;
        gridBagConstraints.weightx = 1.0;
        gridBagConstraints.weighty = 4.0;
        add(jScrollPane5, gridBagConstraints);

    }//GEN-END:initComponents
    
    /** Getter for property identity.
     * @return Value of property identity.
     *
     */
    public identity getIdentity() {
        return this.identity;
    }
    
    /** Setter for property identity.
     * @param identity New value of property identity.
     *
     */
    public void setIdentity(identity identity) {
        this.identity = identity;
        updateDrugView();
        updateProblemView();
    }
    
    void updateDrugView() {
        drugModel.setList( drugModel.getFactory().getConvertedList());
        drugModel.newObject();
        //       drugModel.fireTableDataChanged();
    }
    
    void updateProblemView() {
        problemModel.setList( problemModel.getFactory().getConvertedList() );
        problemModel.newObject();
    }
    
    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JLabel jLabel3;
    private javax.swing.JLabel jLabel4;
    private javax.swing.JLabel jLabel5;
    private javax.swing.JLabel jLabel6;
    private javax.swing.JLabel jLabel7;
    private javax.swing.JLabel jLabel8;
    private javax.swing.JPanel jPanel1;
    private javax.swing.JPanel jPanel2;
    private javax.swing.JPanel jPanel3;
    private javax.swing.JPanel jPanel4;
    private javax.swing.JPanel jPanel5;
    private javax.swing.JPanel jPanel6;
    private javax.swing.JScrollPane jScrollPane1;
    private javax.swing.JScrollPane jScrollPane2;
    private javax.swing.JScrollPane jScrollPane3;
    private javax.swing.JScrollPane jScrollPane4;
    private javax.swing.JScrollPane jScrollPane5;
    private javax.swing.JScrollPane jScrollPane6;
    private javax.swing.JScrollPane jScrollPane7;
    private javax.swing.JScrollPane jScrollPane8;
    private javax.swing.JScrollPane jScrollPane9;
    private javax.swing.JSplitPane jSplitPane1;
    private javax.swing.JSplitPane jSplitPane2;
    private javax.swing.JSplitPane jSplitPane3;
    private javax.swing.JTable jTable2;
    private javax.swing.JTable jTable3;
    private javax.swing.JTable jTable4;
    private javax.swing.JTable jTable5;
    private javax.swing.JTextArea jTextArea1;
    private javax.swing.JTextArea jTextArea2;
    private javax.swing.JTextArea jTextArea3;
    private javax.swing.JTextArea jTextArea4;
    private javax.swing.JTextField jTextField1;
    private javax.swing.JTextField jTextField2;
    private javax.swing.JTextField jTextField3;
    private javax.swing.JTextField jTextField4;
    private javax.swing.JTextField jTextField5;
    private quickmed.usecases.test.TableWithPopup tableWithPopup1;
    private quickmed.usecases.test.TableWithPopup tableWithPopup2;
    // End of variables declaration//GEN-END:variables
    //    TableCellEditor testDrugEditor;
    
    /** Holds value of property identity. */
    private identity identity;
    
}
