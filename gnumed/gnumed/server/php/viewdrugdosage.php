<?php

include ('drugbegin.php');
?>

<h2>Dosage Recommendations</h2>


<table><tr><th>Route</th><th>Category</th><th>Dose</th><th>Hints</th><th></th><th></th></tr>

<?php
  $result = pg_query (<<<EOD
select coalesce ((select description from drug_warning_categories dwc where dwc.id = id_drug_warning_categories), '') as dwc, 
       drug_routes.description as dr, 
       dosage_hints,
	drug_dosage.id as id	      
from drug_dosage, drug_routes 
where 
       id_drug = $id and  
       drug_routes.id = id_route 
EOD
); 
  while ($row = pg_fetch_array ($result))
    {
      echo "<tr><td>{$row['dr']}</td><td>{$row['dwc']}</td><td>";

      $result2 = pg_query ("select * from substance_dosage, drug_units where id_drug_dosage = {$row['id']} and drug_units.id = id_unit");
      while ($row2 = pg_fetch_array ($result2))
	{
	  if ($row2["dosage_type"] == 'w')
	    $per = '/kg';
	  else 
	    if ($row2["dosage_type"] == 's')
	      $per = '/m2';
	    else
	      if ($row2["dosage_type"] == 'a')
		$per = '/age (months}';
	      else
		$per = '';
	  $per = $row2["unit"] . $per;
	  echo "{$row2['dosage_start']}{$per}-{$row2['dosage_max']}{$per}";
	}

      echo "</td><td>{$row['dosage_hints']}</td>";
      echo "<td><a onClick=\"return confirm('Are you sure?');\" href=\"del_dosage.php?id=$id&dosage_id={$row['id']}\"><small>DEL</small></a></td>";
      echo "<td><a href=\"comment.php?id={$row['id']}&table=drug_dosage\"><small>COMMENT</small></a></td>";
    }
?>
</table>


<h3>New Dosage</h3>
  
<form action="new_dosage.php" method="post">
<input type="hidden" name="id" value="<?= $id ?>">
Start:<input type="text" name="start" size="3">
Max:<input type="text" name="max" size="3">
<select name="unit">
<?php
  $result = pg_query ("select * from drug_units");
  while ($row = pg_fetch_array ($result))
    {
      echo "<option value=\"{$row['id']}\">{$row['unit']}";
    }
?>
</select>
<select name="route">
<?php
  $result = pg_query ("select * from drug_routes");
  while ($row = pg_fetch_array ($result))
    {
      echo "<option value=\"{$row['id']}\">{$row['description']}";
    }
?>
</select>
<select name="type">
<option value="*" selected>Normal
<option value="w">By Weight (kg)
<option value="s">By Surface Area (m2)
<option value="a">By Age (months)
</select>
<select name="warning">
<option value="-1" selected>No warning
<?php
  $result = pg_query ("select * from drug_warning_categories");
  while ($row = pg_fetch_array ($result))
    {
      echo "<option value=\"{$row['id']}\">{$row['description']}";
    }
?>
</select><p>
Hints:<p>
<textarea name="hints" rows="4" cols="50"></textarea><p>
<input type="submit" value="submit">
</form><p>

<a href="drugelement.php?id=<?= $id ?>">Back</a>

</body></html>
