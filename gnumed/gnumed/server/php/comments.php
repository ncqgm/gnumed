<?php

if (! $conn)
     include ('connect.php');

?>

<html><title>Comments</title>

<body>

<?php
$result = pg_query ("select stamp, who from audit where table_name = '$table' and table_row = '$id' and stamp = min (stamp)");
$created = pg_fetch_row ($result);
$result = pg_query ("select stamp, who, version from audit where table_name = '$table' and table_row = '$id' and stamp = max (stamp) and action = 'u'");
$now = pg_fetch_row ($result);
echo "<b>Created By:</b> {$created[0]} <b>on</b> {$created[1]}<P>";
if ($row[2] != 1)
     echo "<b>Latest version:</b> {$now[2]} <b>modified by</b> {$now[1]} <b>on</b> {$now[0]}<p>";
?>

<table>
<tr><th>Date</th><th>User</th><th>Comment</th><th>Version</th><th>Source</th></tr>

<?php

$result = pg_query ("select audit.*, description from audit, info_reference where info_reference.id = source and action = 'v' and table_name = '$table' and table_row = $id order by stamp");
while ($row = pg_fetch_array ($result))
{
  echo "<tr><td>{$row['stamp']}</td><td>{$row['who']}</td><td>{$row['why']}</td><td>{$row['version']}</td><td>{$row['description']}</td></tr>";
}

?></table>

<h2>New Comment</h2>

<form action="new_comment.php" method="post">
<input type="hidden" name="table" value="<?= $table ?>">
<input type="hidden" name="id" value="<?= $id ?>">
<textarea rows=7 cols=50 name="why">
</textarea><p>
<select name="id_info">
<?php
$result = pg_query ("select * from info_reference");
while ($row = pg_fetch_array ($result))
{
  echo "<option value=\"{$row['id']}\">{$row['description']}";
}
?></select>
<input type="submit" value="submit">
</form>

</body></html>




