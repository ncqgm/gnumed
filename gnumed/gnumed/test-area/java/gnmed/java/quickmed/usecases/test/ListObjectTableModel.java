/*
 * ListObjectTableModel.java
 *
 * Created on 3 August 2003, 18:14
 */

package quickmed.usecases.test;
import javax.swing.*;
import javax.swing.table.*;
import java.util.*;
import java.util.logging.*;
import java.beans.*;
import java.lang.reflect.*;
import java.text.*;
/**
 *
 * @author  sjtan
 */
public class ListObjectTableModel  extends AbstractTableModel {
    static Logger logger = Logger.global;
    /** Holds value of property list. */
    private java.util.List list = new ArrayList();
    
    /** Holds value of property columnPropertyDescriptors. */
    private PropertyDescriptor[] columnPropertyDescriptors;
    
    /** Holds value of property beanClass. */
    private Class beanClass;
    
    /** Holds value of property lastValue. */
    private Object lastValue;
    
    /** Utility field used by bound properties. */
    private java.beans.PropertyChangeSupport propertyChangeSupport =  new java.beans.PropertyChangeSupport(this);
    
    /** Holds value of property row. */
    private int row;
    
    /** Holds value of property col. */
    private int col;
    
    /** Holds value of property lastProperty. */
    private String lastProperty;
    
    /** Holds value of property factory. */
    private Factory factory;
    
    /** Holds value of property oldValue. */
    private Object oldValue;
    
    /** Holds value of property defaultEditorsLoaded. */
    private boolean defaultEditorsLoaded;
    
    /** Creates a new instance of ListObjectTableModel */
    public ListObjectTableModel() {
    }
    
    public int getColumnCount() {
        if (getColumnPropertyDescriptors() == null)
            return 1;
        return getColumnPropertyDescriptors().length;
    }
    
    public int getRowCount() {
        if (getList() == null)
            return 1;
        return getList().size();
    }
    
    public Object getValueAt(int rowIndex, int columnIndex) {
        if (getColumnPropertyDescriptors() == null)
            return null;
        if (getList() == null)
            return null;
        try {
//            setRow(row);
//            setCol(col);
            Object o = getList().get(rowIndex);
            PropertyDescriptor pd = getColumnPropertyDescriptors()[columnIndex];
            return pd.getReadMethod().invoke(o,  new Object[0]);
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
    
    public void setValueAt(Object value) {
        logger.info("USING STORED ROW = " + getRow() + " STORED COL= " + getCol());
        setValueAt(value, getRow(), getCol());
    }
    
    public void setValueAt(Object value, int row, int col) {
        Object o = getList().get(row);
        try {
            PropertyDescriptor pd = getColumnPropertyDescriptors()[col];
            Class type = pd.getPropertyType();
            if (  Number.class.isAssignableFrom(type) && value instanceof String) {
                Method m = type.getMethod("decode", new Class[] { String.class } );
                value =  m.invoke(type, new Object[] { value });
            }
            java.util.logging. Logger.global.info("INVOKING ON " + o + " With Value=" + value +
            "with method " + pd.getWriteMethod().getName() );
            Object oldValue = pd.getReadMethod().invoke( o, new Object[0]);
            pd.getWriteMethod().invoke(o, new Object[] { value } );
            setLastProperty(pd.getName());
            setLastValue(value);
            setOldValue(oldValue);
            setRow(row);
            setCol(col);
            fireTableCellUpdated(row,col);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    public boolean isCellEditable(int row, int col) {
        //        if (col == 0)
        //            return false;
        setRow(row);
        setCol(col);
        return true;
    }
    
    public String getColumnName(int column ) {
        return getColumnPropertyDescriptors()[column].getName();
    }
    /** Getter for property list.
     * @return Value of property list.
     *
     */
    public java.util.List getList() {
        return this.list;
    }
    
    public void add( Object o) {
        if (getBeanClass().isAssignableFrom(o.getClass())) {
            getList().add(o);
            fireTableDataChanged();
            
        }
    }
    /** Setter for property list.
     * @param list New value of property list.
     *
     */
    public void setList(java.util.List list) {
        this.list = list;
    }
    
    /** Getter for property setColumnPropertyDescriptors.
     * @return Value of property setColumnPropertyDescriptors.
     *
     */
    public PropertyDescriptor[] getColumnPropertyDescriptors() {
        return this.columnPropertyDescriptors;
    }
    
    /** Setter for property setColumnPropertyDescriptors.
     * @param setColumnPropertyDescriptors New value of property setColumnPropertyDescriptors.
     *
     */
    public void setColumnPropertyDescriptors(PropertyDescriptor[] columnPropertyDescriptors) {
        this.columnPropertyDescriptors = columnPropertyDescriptors;
    }
    
    /** Getter for property beanClass.
     * @return Value of property beanClass.
     *
     */
    public Class getBeanClass() {
        return this.beanClass;
    }
    
    /** Setter for property beanClass.
     * @param beanClass New value of property beanClass.
     *
     */
    public void setBeanClass(Class beanClass) {
        this.beanClass = beanClass;
        try {
            PropertyDescriptor[] pds = Introspector.getBeanInfo(beanClass).getPropertyDescriptors();
            setColumnPropertyDescriptors(pds);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    public void setVisibleProperties( Class beanClass, String[] propertyNames) throws Exception {
        setBeanClass(beanClass);
        
        PropertyDescriptor[] pds = Introspector.getBeanInfo(beanClass).getPropertyDescriptors();
        Map map = new HashMap();
        for (int i = 0; i < pds.length; ++i) {
            map.put( pds[i].getName(), pds[i]);
        }
        List l = new ArrayList();
        for ( int i = 0; i < propertyNames.length; ++i) {
            l.add( map.get(propertyNames[i]) );
        }
        setColumnPropertyDescriptors((PropertyDescriptor[])l.toArray( new PropertyDescriptor[0]));
    }
    
    public int getColumnByName(final java.lang.String name) {
        for (int i = 0; i < getColumnPropertyDescriptors().length; ++i) {
            if (getColumnPropertyDescriptors()[i].getName().equals(name))
                return i;
        }
        return -1;
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
    
    /** Getter for property lastValue.
     * @return Value of property lastValue.
     *
     */
    public Object getLastValue() {
        return this.lastValue;
    }
    
    /** Setter for property lastValue.
     * @param lastValue New value of property lastValue.
     *
     */
    public void setLastValue(Object lastValue) {
        Object oldLastValue = this.lastValue;
        this.lastValue = lastValue;
        propertyChangeSupport.firePropertyChange("lastValue", oldLastValue, lastValue);
    }
    
    /** Getter for property row.
     * @return Value of property row.
     *
     */
    public int getRow() {
        return this.row;
    }
    
    /** Setter for property row.
     * @param row New value of property row.
     *
     */
    public void setRow(int row) {
        this.row = row;
    }
    
    /** Getter for property col.
     * @return Value of property col.
     *
     */
    public int getCol() {
        return this.col;
    }
    
    /** Setter for property col.
     * @param col New value of property col.
     *
     */
    public void setCol(int col) {
        this.col = col;
    }
    
    /** Getter for property lastProperty.
     * @return Value of property lastProperty.
     *
     */
    public String getLastProperty() {
        return this.lastProperty;
    }
    
    /** Setter for property lastProperty.
     * @param lastProperty New value of property lastProperty.
     *
     */
    public void setLastProperty(String lastProperty) {
        String oldLastProperty = this.lastProperty;
        this.lastProperty = lastProperty;
        propertyChangeSupport.firePropertyChange("lastProperty", oldLastProperty, lastProperty);
    }
    
    public void newObject() {
        add(getFactory().newInstance());
    }
    
    public void loadDefaultEditors( TableColumnModel model) {
        PropertyDescriptor[] pd = getColumnPropertyDescriptors();
        for (int i = 0; i < pd.length; ++i) {
            if (Date.class.isAssignableFrom(pd[i].getPropertyType()) )
                model.getColumn(i).setCellEditor( new ShortDateCellEditor() );
        }
    }
    
    /** Getter for property factory.
     * @return Value of property factory.
     *
     */
    public Factory getFactory() {
        return this.factory;
    }
    
    /** Setter for property factory.
     * @param factory New value of property factory.
     *
     */
    public void setFactory(Factory factory) {
        this.factory = factory;
        setBeanClass(factory.newInstance().getClass());
        if ( LimitedViewable.class.isAssignableFrom(getBeanClass())) {
            setViewFromLimitedViewable((LimitedViewable) factory.newInstance());
        }
    }
    
    void setViewFromLimitedViewable( LimitedViewable lv ) {
        try {
            setVisibleProperties(lv.getClass(), lv.getLimitedView() );
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    /** Getter for property oldValue.
     * @return Value of property oldValue.
     *
     */
    public Object getOldValue() {
        return this.oldValue;
    }
    
    /** Setter for property oldValue.
     * @param oldValue New value of property oldValue.
     *
     */
    public void setOldValue(Object oldValue) {
        this.oldValue = oldValue;
    }
    
    /** Getter for property defaultEditorsLoaded.
     * @return Value of property defaultEditorsLoaded.
     *
     */
    public boolean isDefaultEditorsLoaded() {
        return this.defaultEditorsLoaded;
    }
    
    /** Setter for property defaultEditorsLoaded.
     * @param defaultEditorsLoaded New value of property defaultEditorsLoaded.
     *
     */
    public void setDefaultEditorsLoaded(boolean defaultEditorsLoaded) {
        this.defaultEditorsLoaded = defaultEditorsLoaded;
    }
    
}
