<?php

function parse ($text, $tags)

{
  while (list ($key, $value) = each ($tags['escape'])) // escape various strings
    {
      $text = str_replace ($key, $value, $text);
    }
  $text = ereg_replace ("[^\"](http://[A-Za-z0-9\\./_]+)\\[(.+)]", $tags['named_url'], $text);
  $text = ereg_replace ("\\[([A-Za-z0-9_]+\\.jpg)]", $tags['image'], $text);
  $text = ereg_replace ("\\[([A-Za-z0-9_]+\\.png])", $tags['image'], $text);
  $text = ereg_replace ("\\[([A-Za-z0-9_]+\\.gif])", $tags['image'], $text);
  $text = ereg_replace ("\\[see:(.+)]", $tags['xref'], $text);
  $text = ereg_replace ("[^\"](http://[A-Za-z0-9\\./_]+)", $tags['url'], $text);
  $text = ereg_replace ("\\*\\*([^\\.\\*<]{1,40})\\*\\*", $tags['bold'], $text);
  $text = ereg_replace ("\\*([^\\.\\*<]{1,40})\\*", $tags['italic'], $text);
  $text = ereg_replace ("``([^<]{1,40})``", $tags['tt'], $text);
  $lines = explode ("\n", $text);
  $mode = 0; // 0=normal 1=quote 2=list 3=table
  $out = array ();
  $newpara = 1;
  while (list ($i, $line) = each ($lines))
    {
      if (strlen ($line) < 2 && ! $newpara)
	{
	  switch ($mode)
	    {
	    case 1:
	      $out[] = $tags['endquote'];
	      break;
	    case 2:
	      $out[] = $tags['endlist'];
	      break;
	    case 3:
	      $out[] = $tags['endtable'];
	      break;
	    }
	  $out[] = $tags['para'];
	  $mode = 0;
	  $newpara = 1;
	}
      else
	{
	  $newpara = 0;
	  if ($line[0] == "-" && $line[1] == " ")
	    {
	      switch ($mode)
		{
		case 0:
		  $mode = 2;
		  $out[] = $tags['beginlist']; // starting a new list
		  $out[] = $tags['list_item'] . substr ($line, 2);
		  break;
		case 1:
		  $out[] = $line;
		  break;
		case 2:
		  $out = $tags['list_item'] . substr ($line, 2); // list item in a list
		  break;
		}
	    }
	  else if ($line[0] == "|")
	    {
	      if ($mode != 3)
		{
		  $out[] = $tags['begintable'];
		  $mode = 3;
		}
	      $line = substr ($line, 1, -1);
	      $line = str_replace ("|", $tags['tabledivisor'], $line);
	      $out[] = $tags['tablerowstart'] . $line . $tags['tablerowend'];
	    }
	  else if ($line[0] == " ")
	    {
	      if ($mode == 0) // indentation in normal mode, move to quotation 
		{
		  $mode = 1; 
		  $out[] = $tags['beginquote'];
		}
	      $out[] = substr ($line, 1);
	    }
	  else
	    {  
	      // normal text ends up here
	      switch ($mode)
		{
		case 1:
		  $out[] = $tags['endquote'];
		  break;
		case 2:
		  $out[] = $tags['endlist'];
		  break;
		case 3:
		  $out[] = $tags['endtable'];
		  break;
		}
	      $mode = 0;
	      $out[] = $line;
	    }
	} // else if strlen () < 2
    } // while $lines
  return implode ("\n", $out);
} // function parse ()

?>