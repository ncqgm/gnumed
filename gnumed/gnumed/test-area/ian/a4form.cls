% LaTeX environment for forms
% Usage:
% each page of the form is wrapped in \begin{page}....\end{page}.
% within this environment 3 commands are available
%     \lineh{xx}{yy}{ll} Draws horizontal line x= millimetres from left hand side of page
%     y= millimetres from the top, ll length of line in millimetres
%     \linev{xx}{yy}{ll} Draws vertical line
%     \text{xx}{yy}{ll}{tt} Drwas  text tt at the position (xx, yy) ll is the maximum length, 
% after which lines are wrapped. most latex commands are accepted in tt.

% \field{f} in the input to \text, queries gnumed for the value of field f and replaces itself
% with this value
% \checkbox {c} draws a small rectangle and the label c. Then queries gnumed for field c. if
% gnumed returns true, draws a bullet in the rectangle 


\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{a4form}[2003/11/15 A4 forms class]

\LoadClass[a4paper]{minimal}
% use 12pt as default
% FIXME: provide a way to change font size
\renewcommand{\normalsize}{\fontsize{12pt}{12pt}\selectfont}
% zero ``hard margins'' which default to 1 inch
\setlength{\hoffset}{-1in}
\setlength{\voffset}{-1in}
% zero 'soft margins''
\setlength{\parindent}{0pt}
% set A4 size
\setlength{\textwidth}{210mm}
\setlength{\textheight}{295mm}

% our environment is really a picture environment covering the entire page
\newenvironment{page}{\setlength{\unitlength}{1mm} \begin{picture}(210,295)(0,-295)}{\end{picture}}

% horiztional lines. Note Y is negative so coordinates are ``right''
\DeclareRobustCommand{\lineh}[3]{\put(#1,-#2){\line(1,0){#3}}}
% vertical lines
\DeclareRobustCommand{\linev}[3]{\put(#1,-#2){\line(0,-1){#3}}}
% text at arbitary position. Use parbox to provide word wrapping
\DeclareRobustCommand{\text}[4]{\put(#1,-#2){
\parbox[t]{#3 mm}{#4}
}}

% checbox. Emits a request as :Cxxxxx= on stdout, where xxxxx is the
% checkbox label. Expects 1 or 0 on stdin.
\DeclareRobustCommand{\checkbox}[1]{\typeout{:C#1=} \read-1 to \flag
\ifnum\flag>0 \framebox(3,3){$\bullet$} \else \framebox(3,3){} \fi #1}

% string field. Emits field name on stdout as :Fxxxxx= where xxxxx is the
% field name, expects the value on stdin
\DeclareRobustCommand{\field}[1]{\typeout{:F#1=} \read-1 to \n 
\n
}


