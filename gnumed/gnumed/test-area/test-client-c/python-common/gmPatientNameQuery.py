# Function to form a SQL query from a search string.
# Separated out for easy hacking (and cross-client use)

from string import *
#import gmI18N
_ = lambda x:x

def MakeQuery (name):
    names = split (lower (name))
    if len (names) == 0:
        return "select -1, 'Invalid Query' as Error"
    extraquery = ""
    
    if names[-1][0] == "<":
        extraquery = " and interval (identity.dob) < "
    if names[-1][0] == ">":
        extraquery = " and interval (identity.dob) > "
    if len (extraquery) > 0:
        try:
            age = int (names[-1][1:])
            extraquery = extraquery + str (age) + " years"
        except ValueError:
            extraquery = ""
        del names[-1]
    else:
        try:
            yob = int (names[-1])
            del names[-1]
            if yob < 1860:
                # must be age
                extraquery = " and interval (identity.dob) = %d years" % yob
            else:
                extraquery = " and extract (year from identity.dob) = %d" % yob
        except ValueError:
            pass
    
    if len (names) > 1:
        # now look for comma
        comma = -1
        for i in range (0, len(names)-1):
            if names[i][-1] == ',':
                names[i] = names[i][:-1]
                comma = i
        if comma > -1:
            lastnames = join (names[:i+1])
            firstnames = join (names[i+1:])
        else:
            firstnames = names[0]
            lastnames = join (names[1:])
    if len(names) == 1:
        lastnames = names[0]
        firstnames = ""
    if len (names) == 0:
        lastnames = ""
        firstnames = ""
    if lastnames == "?":
        lastnames = ""
    lastnames = lastnames + "%"
    firstnames = firstnames + "%"
    query = """
select identity.id, names.title, names.firstnames as %s, names.lastnames as %s, to_char (identity.dob, 'DD/MM/YY') as %s
from
 identity, names
where names.firstnames ilike '%s' and names.lastnames ilike '%s'
and identity.id = names.id_identity %s
""" % (_("Surname"), _("Name"), _("DOB"), firstnames, lastnames, extraquery)
    return query
               
if __name__ == '__main__':
    print MakeQuery ("Haywood, Ian <40")
    print MakeQuery ("Ian Haywood")
    print MakeQuery ("Haywood")
    print MakeQuery ("?, Ian 1977")
    
    
