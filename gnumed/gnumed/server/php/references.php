<?php

if (! $conn)
     include ('connect.php');

?>

<html><title>References</title>

<body>
<h1>References</h1>

<table>
<tr><th>Name</th><th>Type</th><th></th></tr>
<?php

$result = pg_query ("select * from info_reference");
while ($row = pg_fetch_array ($result))
{
  echo "<tr><td>{$row['description']}</td><td>";
  if ($row['source_category'] == 'p')
    echo "peer-review";
  if ($row['source_category'] == 'a')
    echo "official authority";  
  if ($row['source_category'] == 'i')
    echo "independent";  
  if ($row['source_category'] == 'm')
    echo "manufacturer";  
  if ($row['source_category'] == 'o')
    echo "other";  
  if ($row['source_category'] == 's')
    echo "self-defined";
  echo "</td></tr>";
} 
?></table>

<h2>New Reference</h2>

<form action="new_ref.php" method="post">
<input type="text" name="description" size="30">
<select name="source_category">
<option value="p">peer-review
<option value="a">official authority
<option value="i">independent
<option value="m">manufacturer
<option value="o">other
<option value="d">self-defined
</select>
<input type="submit" value="submit">
</form>

</body></html>
