import time
import string

def checkStrDate(val):
        if ( string.strip(val) == ''):
                return ''

        try:
                t = time.strptime(val, '%Y')
                ta = list(t)
                ta[1],ta[2] = 1,1
                return time.strftime(  '%d/%m/%Y', ta)
        except:
                pass
        try:
                t = time.strptime(val, '%x')
                return val
        except:
                pass
        for x in (  '%x', '%d/%m/%Y','%d/%m/%y', '%d-%h-%Y', '%d-%h-%y', '%d-%m-%y', '%d-%m-%Y'):
                try:
                        t = time.strptime(val, x)
                        return time.strftime( '%d/%m/%Y', t)
                except:
                        pass
        for x in ( '%h %Y','%h-%Y','%h/%Y', '%m-%y','%m/%Y', '%m/%Y', '%m/%y', '%h-%y', '%h %y'):
                try:
                        t = time.strptime(val, x)
                        ta = list(t)
                        ta[2] = 1
                        return time.strftime(  '%d/%m/%Y', ta)
                except:
                        raise TypeError('date format not recognized')



