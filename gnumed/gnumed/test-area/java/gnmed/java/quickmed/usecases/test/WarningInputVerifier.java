/*
 * WarningInputVerifier.java
 *
 * Created on 14 April 2003, 01:06
 */

package quickmed.usecases.test;
import javax.swing.JOptionPane;
import javax.swing.JComponent;
import javax.swing.SwingUtilities;

/**
 *
 * @author  sjtan
 */
public abstract class WarningInputVerifier extends javax.swing.InputVerifier {
    
    /** Holds value of property warning. */
    private boolean warning;
    
    
    
    /** Creates a new instance of MonthYearInputVerifier */
    public WarningInputVerifier() {
    }
    
    /** Checks whether the JComponent's input is valid. This method should
     * have no side effects. It returns a boolean indicating the status
     * of the argument's input.
     *
     * @param input the JComponent to verify
     * @return <code>true</code> when valid, <code>false</code> when invalid
     * @see JComponent#setInputVerifier
     * @see JComponent#getInputVerifier
     *
     *
     */
    public abstract boolean verify(final JComponent input) ;
    public abstract String getWarningString();
    
    void displayWarning(final  JComponent input) {
        if ( !isWarning() ) {
            setWarning(true);
        SwingUtilities.invokeLater( new Runnable() {
            public void run() {
                JOptionPane.showMessageDialog(
                SwingUtilities.getRootPane(
                input
                )
                ,getWarningString(),
                "Input Error", JOptionPane.ERROR_MESSAGE);
                setWarning(false);
            }
        } );
        }
        
    }
    
    public boolean shouldYieldFocus(JComponent input) {
        if (!verify(input)) {
            displayWarning(input);
        }
        return super.shouldYieldFocus(input);
    }
    
    /** Getter for property warning.
     * @return Value of property warning.
     *
     */
    public synchronized boolean isWarning() {
        return this.warning;
    }    
    
    /** Setter for property warning.
     * @param warning New value of property warning.
     *
     */
    public synchronized void setWarning(boolean warning) {
        this.warning = warning;
    }

   
    
}
