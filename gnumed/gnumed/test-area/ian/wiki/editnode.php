<?php

mysql_pconnect ('localhost', 'ian', 'angmar');
mysql_query ('use docwiki');

if ($HTTP_GET_VARS['node'])
{
  $node = $HTTP_GET_VARS['node'];
  $result  = mysql_query ("select * from node where id = $node");
  $row = mysql_fetch_array ($result);
}
else
{
  $row['title'] = "New Document";
  $row['contents'] = "";
  $row['author'] = "";
  $up = $HTTP_GET_VARS['up'];
  $prev= $HTTP_GET_VARS['prev'];
  $next = $HTTP_GET_VARS['next'];
}

?>

<html>
<head><title>Editing <? echo $row['title']; ?></title></head>
<body>
<h1>Editor</h1>
<form action="submitnode.php" method="post">
Title: <input type="text" name="title" value="<? echo $row['title']; ?>" size=20><p>
Author: <input type="text" name="author" value="<? echo $row['author']; ?>" size=20><p>
<textarea  rows=25 cols=80 wrap="virtual" name="contents">
<? echo $row['contents']; ?>
</textarea><p>
<input type="submit" name="Submit"><a href="help.html">Help</a><p>
<?php
if (! $HTTP_GET_VARS['node'])
{
  echo "<input type=\"hidden\" name=\"up\" value=\"$up\">";
  if ($prev || $prev == 0)
    echo "<input type=\"hidden\" name=\"prev\" value=\"$prev\">";
  if ($next)
    echo "<input type=\"hidden\" name=\"next\" value=\"$next\">";
}
else
{
  echo "<input type=\"hidden\" name=\"node\" value=\"$node\">";
}
?>
</form>
</body>
</html>



