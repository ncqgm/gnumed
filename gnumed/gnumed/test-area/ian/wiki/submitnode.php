<?php

mysql_pconnect ('localhost', 'ian', 'angmar');
mysql_query ('use docwiki');

$title = str_replace ("'", "''", $HTTP_POST_VARS['title']);
$contents = str_replace ("'", "''", $HTTP_POST_VARS['contents']);
$author = str_replace ("'", "''", $HTTP_POST_VARS['author']);

if ($HTTP_POST_VARS['node'])
{
  $node = $HTTP_POST_VARS['node'];
  mysql_query ("update node set title='$title', author='$author', contents='$contents' where id=$node");
}
else
{
  $up = $HTTP_POST_VARS['up'];
  echo 'Up: ' . $up ."\n";
  echo 'Prev: ' . $HTTP_POST_VARS['prev']. "\n";
  if ($HTTP_POST_VARS['prev'])
    $prev= $HTTP_POST_VARS['prev'];
  else
    {
      if ($HTTP_POST_VARS['prev'] == 0)
	$prev = 'NULL';
      else
	{
	  $next = $HTTP_POST_VARS['next'];
	  // grab next's prev, which becomes our prev
	  $result = mysql_query ("select prev from node where id=$next");
	  $prev = mysql_fetch_array ($result);
	}
    }

  echo "insert into node (title, contents, author, up, prev) values ('$title', '$contents', '$author', $up, $prev)";
  $node = mysql_insert_id ();
  if ($HTTP_POST_VARS['next'])
    mysql_query ("update node set prev=$node where id=$next"); // update the next node to point to us.
  else
    mysql_query ("update node set prev=$node where prev=$prev");
}
?>

<html>
<head>
  <title>Redirecting.......</title>
  <http-equiv="refresh" content="1;URL=viewnode.php?node=<? echo $node;?>">
</head>
 <body></body>
</html>