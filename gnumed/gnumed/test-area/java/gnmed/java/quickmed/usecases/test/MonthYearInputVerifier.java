/*
 * MonthYearInputVerifier.java
 *
 * Created on 14 April 2003, 00:13
 */

package quickmed.usecases.test;
import javax.swing.JOptionPane;
import javax.swing.JComponent;
import javax.swing.SwingUtilities;

/**
 *
 * @author  sjtan
 */
public class MonthYearInputVerifier extends WarningInputVerifier {
    private static  java.text.DateFormat formatter;
    
    
    static {
        formatter = new java.text.SimpleDateFormat("M/y");
    };
    
    /** Creates a new instance of MonthYearInputVerifier */
    public MonthYearInputVerifier() {
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
    public boolean verify(final JComponent input) {
        
        try {
            String text = ((javax.swing.text.JTextComponent)input).getText();
            formatter.parse(text);
        } catch (java.text.ParseException pe) {
            return false;
        }
        return true;
    }
    
    public String getWarningString() {
        return "Please Enter in mm/yy format";
    }
    
}
