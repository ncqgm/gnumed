<!--
PHP interface to gnumed drug database
Copyright (C) 2002 Ian Haywood 

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
or see online at http://www.gnu.org/licenses/gpl.html
!>


<html>
<title>Classes</title>
<body>
<?
pg_connect ("dbname=gmdrugs user=ian");
$list = pg_query ("select * from drug_class order by description");
while ($row = pg_fetch_array ($list))
{
  echo "<a href=\"viewelement.php?id=" . $row['id'] ."\">" . $row['description'];
  echo "</a>";
  if ($row['category'] == 't')
    {
      echo "<small>(Therapeutic)</small>";
    }
  else
    {
      echo "<small>(Pharmaceutic)</small>";
    }
  echo "<P>";
}

?>

<h2>Add New Class</h2>

<form action="newclass.php" method="post">
Name: <input type="text" name="newname" size="20">
<input type="radio" name="type" value="t">Therapeutic
<input type="radio" name="type" value="p" checked>Pharmaceutic
<P>
<input type="submit" value="submit">
</form>

</body>
</html>

