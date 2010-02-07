"""
Copyright (C) 2006 author 

    This program is free software; you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
	    the Free Software Foundation; either version 2 of the License, or
	        (at your option) any later version.

		    This program is distributed in the hope that it will be useful,
		        but WITHOUT ANY WARRANTY; without even the implied warranty of
			    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
			        GNU General Public License for more details.


"""
import string
def decrypt(f2, password):
   #print "password is", password
   while password[-1] in string.whitespace:
       password = password[:-1]

   if f2 and len(f2) and f2[0] ==' ':
      return f2
   p = password
   l2 = []
   for j in range(len(f2) / len(p) +1 ) :
       l = ''.join([ chr ( (ord( f2[i+j*len(p)] ) - ord(p[i])) % 256 ) 
                  for i in range( min(len(p), len(f2)-j*len(p))) ])
       l2.append(l)

   return ''.join(l2)
