<?php
mysql_pconnect ('localhost', 'ian', 'angmar');
mysql_query ('use docwiki');
if ($HTTP_GET_VARS['node'])
{
  $node = $HTTP_GET_VARS['node'];
  $result  = mysql_query ("select * from node where id = $node");
}
else
{
  $title = $HTTP_GET_VARS['title'];
  $result = mysql_query ("select * from node where title = '$title'");
}
$row = mysql_fetch_array ($result);
if (! $row)
     die ("No such node $node");
$node = $row['id'];
$result = mysql_query ("select id from node where prev = $node");
$row2 = mysql_fetch_array ($result);
if ($row2)
     $next = $row2['id'];
     else
     $next = 0;

include ('parse.php');

$html_tags = array (
		    "escape" => array (
				       "<" => "&lt;",
				       ">" => "&gt;",
				       "&" => "&amp;"
				       ),
		    "named_url" => "<a href=\"\\1\">\\2</a>",
		    "url" => "<a href=\"\\1\">\\1</a>",
		    "image" => "<img src=\"image.php?file=\\1\">",
		    "xref" => "<a href=\"viewnode.php?title=\\1\">\\1<\a>",
		    "bold" => "<b>\\1</b>",
		    "italic" => "<i>\\1</i>",
		    "tt" => "<tt>\\1</tt>",
		    "para" => "<p>",
		    "list_item" => "<li>",
		    "beginlist" => "<ul>",
		    "endlist" => "</ul>",
		    "begintable" => "<table>",
		    "endtable" => "</table>",
		    "tablerowstart" => "<tr><td>",
		    "tablerowend" => "</td></tr>",
		    "tabledivisor" => "</td><td>",
		    "beginquote" => "<pre>\n",
		    "endquote" => "</pre>"
		    );

?>

<html>
<head><title><? echo $row['title']; ?></title></head>
<body>
<table WIDTH="100%" BORDER="0" CELLPADDING="0" CELLSPACING="0">
  <tr><th COLSPAN="3" ALIGN="center">GNUMed Manual</th>
</tr>
  <tr>
     <td WIDTH="10%" ALIGN="left"   VALIGN="bottom">
<?php
if ($row['prev'])
     echo "<a HREF=\"viewnode.php?node=$row[prev]\">Prev</a>";
?>
     </td><td WIDTH="80%" ALIGN="center" VALIGN="bottom">
<?php
if ($row['up'])
     echo "<a HREF=\"viewnode.php?node=$row[up]\">Up</a>";
?>
     </td><td WIDTH="10%" ALIGN="right"  VALIGN="bottom">
<?php
if ($next)
     echo "<a HREF=\"viewnode.php?node=$next\">Next</a>";
?>
  </td></tr>
<tr>
     <td WIDTH="10%" ALIGN="left"   VALIGN="bottom">
<?php
  if ($row['up'])
     echo "<a HREF=\"editnode.php?up=$row[up]&next=$node\" color=\"red\">[Insert New]</a>";
?>
     </td><td WIDTH="80%" ALIGN="center" VALIGN="bottom">
<a HREF="editnode.php?node=<? echo $row['id']; ?>">[Edit This Page]</a>
  </td><td WIDTH="10%" ALIGN="right"  VALIGN="bottom">
<?php
  if ($row['up'])
     echo "<a HREF=\"editnode.php?up=$row[up]&prev=$node\" color=\"red\">[Insert New]</a>";
?></td></tr>
</table>

<hr ALIGN="LEFT" WIDTH="100%">

<h1><? echo $row['title']; ?></h1>
<ul>
<?php
$lastprev = 0;
$result = mysql_query ("select id, title from node where up = $node");
while (list ($subnode, $title) = mysql_fetch_row ($result))
{
  $lastprev = $subnode;
  echo "<li><a HREF=\"viewnode.php?node=$subnode\">$title</a>\n";
} 
?>
<li><a HREF="editnode.php?up=<? echo $node; ?>&prev=<? echo $lastprev; ?>" color="red">[Add New Page]</a>
</ul>


<?php
echo parse ($row['contents'], $html_tags);
?>

<hr ALIGN="LEFT" WIDTH="100%">

<table WIDTH="100%" BORDER="0" CELLPADDING="0" CELLSPACING="0">
<tr>
     <td WIDTH="10%" ALIGN="left"   VALIGN="top">
<?php
  if ($row['up'])
     echo "<a HREF=\"editnode.php?up=$row[up]&next=$node\" color=\"red\">[Insert New]</a>";
?>
     </td><td WIDTH="80%" ALIGN="center" VALIGN="top">
<a HREF="editnode.php?node=<? echo $row['id']; ?>">[Edit This Page]</a>
  </td><td WIDTH="10%" ALIGN="right"  VALIGN="top">
<?php
  if ($row['up'])
     echo "<a HREF=\"editnode.php?up=$row[up]&prev=$node\" color=\"red\">[Insert New]</a>";
?></td></tr>
<table WIDTH="100%" BORDER="0" CELLPADDING="0" CELLSPACING="0">
  <tr>
     <td WIDTH="10%" ALIGN="left"   VALIGN="bottom">
<?php
if ($row['prev'])
     echo "<a HREF=\"viewnode.php?node=$row[prev]\">Prev</a>";
?>
     </td><td WIDTH="80%" ALIGN="center" VALIGN="bottom">
<?php
if ($row['up'])
     echo "<a HREF=\"viewnode.php?node=$row[up]\">Up</a>";
?>
     </td><td WIDTH="10%" ALIGN="right"  VALIGN="bottom">
<?php
if ($next)
     echo "<a HREF=\"viewnode.php?node=$next\">Next</a>";
?>
  </td></tr>
</table>
</body>
</html>

