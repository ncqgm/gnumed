\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{a4form}[2003/11/15 A4 forms class]

\LoadClass[a4paper]{minimal}
\renewcommand{\normalsize}{\fontsize{12pt}{12pt}\selectfont}
\setlength{\hoffset}{-1in}
\setlength{\voffset}{-1in}
\setlength{\parindent}{0pt}
\setlength{\textwidth}{210mm}
\setlength{\textheight}{295mm}

\newenvironment{page}{\setlength{\unitlength}{1mm} \begin{picture}(210,295)(0,-295)}{\end{picture}}

\DeclareRobustCommand{\lineh}[3]{\put(#1,-#2){\line(1,0){#3}}}
\DeclareRobustCommand{\linev}[3]{\put(#1,-#2){\line(0,-1){#3}}}
\DeclareRobustCommand{\text}[4]{\put(#1,-#2){
\parbox[t]{#3 mm}{#4}
}}
\DeclareRobustCommand{\checkbox}[1]{\typeout{:C#1=} \read-1 to \flag
\ifnum\flag>0 \framebox(3,3){$\bullet$} \else \framebox(3,3){} \fi #1}
\DeclareRobustCommand{\field}[1]{\typeout{:F#1=} \read-1 to \n 
\n
}


