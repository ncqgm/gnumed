Has anyone used a tablet pc (win/linux) for daily use ? 
My dad just told me today that he like many docs won't start to learn typewriting 
So he won't be using the keyboard to enter patient consulatatio notes because it
would be too slow for his cuurent workflow. He still would like to use a PC for
consulatation notes since those  paper charts have gotten way too big.

He was told about tablet PCs by some other doctor. I started to think about it 
and here are my thoughts. Why not combine handwriting with SOAP entry ?
From what I read linux based handwriting recognition is nowhere near as good 
as Bill's. But who cares I thought. What not just store the graphics ? So what 
we would need is a widget made of a way stripped down graphics app like gimp. 
He would simply write on the screen while Gnumed would attach the current date, 
episode, issue and so forth to the picture. The picture itself would then be 
stored in the database. The *empty* initial picture could even be a template 
which imitates the lines of a paper notebook.

Please help me think this through. Is it possible to build a wxwidget for 
graphical input like this?
 _______________________________________
|date	|input area	|input area	|
________________________________________
|date	|input area	|entry		|
 _______________________________________

since those images are black and white they should be very small
Since they contain meta info on date, issue ... the could be displayed later 
just like we would display text.

And guess what there is :-) a solution. One way to make use of this is through
A project called 'piddle' ( piddle.sf.net )

"""
PIDDLE is a Python module for creating two-dimensional graphics in a manner that
is both cross-platform and cross-media; that is, it can support screen graphics 
(e.g. QuickDraw, Windows, Tk) as well as file output (PostScript, PDF, GIF, etc.). 
It makes use of the native 2D drawing calls of each backend, for maximum efficiency 
and quality. It works by defining a base class (piddle.Canvas) with methods for all 
supported drawing primitives. A particular drawing context is provided in the form 
of a derived class. PIDDLE applications will be able to automatically select an 
appropriate backend for the user's environment. 
"""

A backend called wxPiddle is available for download via their base package (included)
and from http://darwin.epbi.cwru.edu/~pjacobs/.

A demo application is provided. 