/*
 * PartyHome.java
 *
 * Created on 04 July 2003, 23:37
 */

package  xgmed.domain.accountability;
import java.util.*;
import xgmed.domain.observation.*;
/**
 *
 * @author  sjtan
 */
public interface PartyHome {
    public PartyType findPartyType(java.lang.String typeName) throws Exception;
    public PartyType createPartyType() throws Exception;
    public void save(PartyType type) throws Exception;
    public List findParty( PartyType type, String name) throws Exception;
    public List findPerson( PartyType type, String lastName, String firstName) throws Exception;
    public List findPerson( PartyType type, java.util.Date birthDate) throws Exception;
    public List findPerson( PartyType type, Measurement low, Measurement high);
}
