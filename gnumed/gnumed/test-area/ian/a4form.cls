% LaTeX environment for forms
% Usage:
% each page of the form is wrapped in \begin{page}....\end{page}.
% within this environment 3 commands are available
%     \lineh{xx}{yy}{ll} Draws horizontal line x= millimetres from left hand side of page
%     y= millimetres from the top, ll length of line in millimetres
%     \linev{xx}{yy}{ll} Draws vertical line
%     \text{xx}{yy}{ll}{tt} Drwas  text tt at the position (xx, yy) ll is the maximum length, 
% after which lines are wrapped. most latex commands are accepted in tt.

% \checkbox {c} draws a small rectangle, with a dot if c is nonzero

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{a4form}[2003/11/15 A4 forms class]

\LoadClass[a4paper]{minimal}
% use 12pt as default
\renewcommand{\normalsize}{\fontsize{12pt}{12pt}\selectfont}
% provide smaller size
\renewcommand{\small}{\fontsize{8pt}{8pt}\selectfont}
% zero ``hard margins'' which default to 1 inch
\setlength{\hoffset}{-1in}
\setlength{\voffset}{-1in}
% zero 'soft margins''
\setlength{\parindent}{0pt}
% set A4 size
\setlength{\textwidth}{210mm}
\setlength{\textheight}{295mm}

% our environment is really a picture environment covering the entire page
\newenvironment{page}{\setlength{\unitlength}{1mm}\begin{picture}(210,295)(0,-295)}{\end{picture}}

% horizontal lines. Note Y is negative so coordinates are ``right''
\DeclareRobustCommand{\lineh}[3]{\put(#1,-#2){\line(1,0){#3}}}
% vertical lines
\DeclareRobustCommand{\linev}[3]{\put(#1,-#2){\line(0,-1){#3}}}
% text at arbitrary position. Use parbox to provide word wrapping
\DeclareRobustCommand{\text}[4]{\put(#1,-#2){
\parbox[t]{#3 mm}{#4}
}}

% checkbox. Box is checked if pased integer greater than zero
\DeclareRobustCommand{\checkbox}[1]{\ifnum#1>0 \framebox(3,3){$\bullet$} \else \framebox(3,3){} \fi}


