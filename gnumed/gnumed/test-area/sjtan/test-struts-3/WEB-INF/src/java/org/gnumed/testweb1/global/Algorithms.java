/*
 * Algorithm.java
 *
 * Created on September 20, 2004, 10:03 AM
 */

package org.gnumed.testweb1.global;
import java.util.*;
/**
 *
 * @author  sjtan
 */
public class Algorithms {
    static Map stopWords;
    static {
        stopWords = new HashMap();
        String[] words = { "and", "or", "the", "a", "an", "is", "has", "," };
        for (int i = 0; i < words.length; ++i) {
            stopWords.put(words[i],words[i]);
        }
        
    }
    
    public static void addStopWord(String word) {
        stopWords.put(word, word);
    }
    
    public static String[] filterOutStopWords( String[] ss) {
        List l = new ArrayList();
        for (int i =0; i < ss.length; ++i) {
            if  ( stopWords.get(ss[i]) != null ) {
                continue;
            }
            l.add(ss[i]);
        }
        
        return (String[]) l.toArray(new String[0]);
        
    }
    
    public static boolean isCharMatchedInWords(String ss1, String ss2, double wordThreshold, double wordCountFraction ) {
        int[] n = findMatchingTokens(ss1, ss2, wordThreshold);
        int min = n[1] < n[2] ? n[1]: n[2];
        return (double)min * wordCountFraction < (double) n[0];
    }
    
    /** this is a O^2 brute-force maximal character in order match algorithm for words in sentences
     *
     *@param threshold  the threshold for character count match.
     *
     *@return an array of int , the first element is the number of matches , the second and third the number of
     *  processed non-stopword tokens in each string.
     */
    public static int[] findMatchingTokens( String ss1, String ss2 , double threshold) {
        
        String[] sa1 = filterOutStopWords( ss1.split("\\s+") );
        String[] sa2 = filterOutStopWords( ss2.split("\\s+") );
        
        
        
        
        boolean[] matched = new boolean[sa2.length];
        for (int i = 0; i < matched.length ; ++i) {
            matched[i] = false;
        }
        int count = 0;
        for (int i = 0 ; i < sa1.length; ++i) {
            for (int j = 0; j < sa2.length; ++j) {
                if (matched[j]) continue;
                String s1 = sa1[i];
                String s2 = sa2[j];
                
                String minS = s1.length() < s2.length() ? s1 : s2;
                String maxS = s1.length() > s2.length() ? s1 : s2;
                String matchS = findInOrderMatchingChars(s1, s2);
                if ( matchS.length() > minS.length() * threshold
                  
                  &&
                minS.length() > maxS.length() * (1-threshold) 
                  
                  ) {
                    
                    matched[j] = true;
                    ++count;
                }
            }
        }
        return new int[] { count, sa1.length, sa2.length };
    }
    
    private static void showSA(String label, String[] sa)  {
        
        System.err.print(label+": " );
        for (int i = 0; i < sa.length;++i) {
            System.err.print(sa[i] + " ");
            
        }
        System.err.println();
        
    }
    
    
    public static String findInOrderMatchingChars( String ss1, String ss2) {
        char[] s1, s2;
        s1 = new char[ss1.length()];
        s2 = new char[ss2.length()];
        ss1.getChars(0, ss1.length(), s1, 0);
        ss2.getChars(0, ss2.length(), s2, 0);
        StringBuffer sb = new StringBuffer();
        if (s2.length < s1.length) {
            char[] tmp = s2; s2 = s1; s1 = tmp;
        }
        
        int j = 0;
        int m=0;
        for ( int i = 0; i < s1.length && j < s2.length; ++i) {
            if (s1[i] == s2[j] ) {
                sb.append(s1[i]);
                ++j;
                ++m;
                continue;
            }
            
            // k will be i that will match nearest j
            for (int k ; j < s2.length; ++j) {
                k=i;
                
                while (++k < s1.length  && s1[k] != s2[j]);
                
                if (k == s1.length)
                    continue;
                
                sb.append(s1[k]);
                i=k ; ++j; ++m;
            }
            
        }
        return sb.toString();
        
        
    }
    
    /** Creates a new instance of Algorithm */
    public Algorithms() {
    }
    
    private static void printIntArray( int[] a) {
        for (int i = 0; i < a.length; ++i) {
            System.err.print(" " +a[i]);
        }
        System.err.println();
    }
    
    
    public static void main(String[] args) {
        
        printIntArray(findMatchingTokens("Charlilee", "Charile", .8));
        
        printIntArray(findMatchingTokens("Headache", "Head ache", .9));
        
        printIntArray(findMatchingTokens("central chest pain", "chest pain", .9));
        
        printIntArray(findMatchingTokens("abdo pain", "abdominal pain", .7));
        
        printIntArray(findMatchingTokens("cough and sore throat , mild fever", "cough , sob and fever", .7));
        
        printIntArray(findMatchingTokens("low back pain", "lumbar back pain", .7));
        
        printIntArray(findMatchingTokens("loin pain, abdo pain persistent", "loin and abdominal pain", .7));
        
        printIntArray(findMatchingTokens("loin pain, abdo pain persistent", "chest and throat pain", .7));
        
        printIntArray(findMatchingTokens("lac arm requires sutures", "review of sutures lac arm", .7));
        
        printIntArray(findMatchingTokens("urti", "hypercholesterolemia", .7));
    }
    
}
