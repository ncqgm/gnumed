\NeedsTeXFormat{LaTeX2e} \ProvidesClass{praxisbrief}
\RequirePackage{ifthen}
\newboolean{@german}     \setboolean{@german}{false}
\DeclareOption{german}{\setboolean{@german}{true}}
\DeclareOption{english}{\setboolean{@german}{false}}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{dinbrief}}


\ExecuteOptions{german} \ProcessOptions
\LoadClass[a4paper,11pt]{dinbrief}
\addresshigh
\setlength{\textheight}{250mm}
\setlength{\topmargin}{2mm}
\setbottomtexttop{265mm}
%\setbottomtexttop{278mm}
%\setaddressoffset{0mm}

\setaddressheight{40mm}
\newcommand{\lettergerman}{}
\newcommand{\letterenglish}{}
\ifthenelse{\boolean{@german}}
       {\RequirePackage{german}\lettergerman}{\letterenglish}

\pagestyle{headings} 
\usepackage [latin1]{inputenc}
\usepackage {latexsym}



\address{\parbox[t]{9cm}{\huge \textbf{Christoph Becker}\\ \small Zahnarzt}
                  \hfill 
                  \parbox[t]{6cm}{Dauner Str. 21\\
                                  53539 Kelberg\\
                                  Tel.: 02692-930023\\
                                  Fax:  02692-930025\\
                                  \small e-Mail: cgbecker@gmx.de\\
                                  

                                  \\ \\
                                   \textbf{Termine nach Vereinbarung\\}
                                   \small Kernarbeitszeit: \\
                                   Mo., Mi., Fr. 8 - 12 Uhr\\
                                   Di., Do. 14 - 19 Uhr\\
                                  }}
\backaddress{Christoph Becker $\cdot$ Dauner Str. 21 $\cdot$ 53539 Kelberg}



%\bottomtext{\parbox[t]{16cm}{\rule [0,3ex]{16cm}{1pt} \small 
\bottomtext{\parbox[t]{16cm}{\rule [0,3ex]{16cm}{0,1mm} \small 
                             \textbf{Bankverbindung:}\\
                             Dt. Apotheker u. Ärztebank, Koblenz \hfill
                             Bankleitzahl: 570 606 12 \hfill
                             Konto: 020 2797003} \\
                             \small StNr.: 13/222/0379/8}
\place{Kelberg}
%\signature{Christoph Becker}
\phone{02692}{-930023}

\centeraddress
%\enabledraftstandard
\nowindowrules
\windowtics
\date{\today}