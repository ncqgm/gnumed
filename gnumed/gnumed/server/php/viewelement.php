<?php
// PHP interface to gnumed drug database
// Copyright (C) 2002 Ian Haywood 

// This program is free software; you can redistribute it and/or
// modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA
// or see online at http://www.gnu.org/licenses/gpl.html

// very complex form for viewing and changing elements
// depends on $id being set either by newclass.php, newdrug.php or from form

include ('drugbegin.php');

?>

<table>

<?php
if ($is_drug)
{
  echo "<tr><td><a href=\"viewnames.php?id=$id\">Name</a></td>";
  echo "<td><a href=\"viewclasses.php?id=$id\">Classes</a></td></tr>";
}

echo "<tr>";

if ($category == 'c')
{
  echo "<td><a href=\"viewcompound.php?id=$id\">Compound</a></td>";
}

?>

<td><a href="viewinter.php?id=<?= $id ?>">Interaction</a></td></tr>
<tr><td><a href="viewdisease.php?id=<?= $id ?>">Disease-Interactions</a></td>
<td><a href="viewadverse.php?id=<?= $id ?>">Adverse Effects</a></td></tr>
<tr><td><a href="viewcaution.php?id=<?= $id ?>">Caution</a></td>
<td><a href="viewinfo.php?id=<?= $id ?>">Information</a></td></tr>
<tr>
<?php
if (! $is_drug) {
  echo "<td><a href=\"viewdrugs.php?id=$id\">Drugs in Class</a></td>";
}
else
{
  if ($category == 's')
    echo "<td><a href=\"viewdrugdosage.php?id=$id\">Dosage</a></td>";
  else
    // compound dosage not yet supported
    echo "<td><a href=\"viewcompounddosage.php?id=$id\">Dosage</a></td>";
}
?>

<?php
if ($category == 'c' or $category == 's')
{
  echo "<td><a href=\"viewproducts.php?id=$id\">Products</a></td>";
}  
else
{
  echo "<td><a href=\"rename_class.php?id=$id\">Rename class</a></td>";
}     
?>

</tr>

</body>
</html>

