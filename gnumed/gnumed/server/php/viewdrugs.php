<?php

include ('drugbegin.php');
?>
<h2>Drugs in This Class</h2>

<?php
  $result = pg_query ("select id_drug, get_drug_name (id_drug) from link_drug_class where id_class = $id");
  while ($row = pg_fetch_row ($result))
  {
    echo "<a href=\"viewelement.php?id={$row[0]}\">{$row[1]}</a><p>";
  }
?>
<h3>New Drug</h3>

<form action="newdrug.php" method="post">
<input type="radio" name="category" value="s">Single drug
<input type="radio" name="category" value="c">Compound<p>
<input type="hidden" name="id_class" value="$id">
<input type="submit">
</form><p>

<a href="viewelement.php?id=<?= $id ?>">Back</a>
</body></html>