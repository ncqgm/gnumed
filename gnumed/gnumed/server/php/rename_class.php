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
$result = pg_query ("select get_drug_name ($id)");
$drugname = pg_fetch_result ($result, 0, 0);

?>

<form action="recv_rename_class.php" method="post">
<input type="hidden" name="id" value="<?= $id ?>">
New name:<input name="name" value="<?= $drugname ?>" size="30">
<input type="submit" value="submit">
</form><p>

<a href="listclasses.php">Back</a>

</body>
</html>

