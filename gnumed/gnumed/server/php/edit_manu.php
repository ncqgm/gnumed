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
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
// or see online at http://www.gnu.org/licenses/gpl.html


if (! $conn)
{
  include ('connect.php');
}

$row = pg_fetch_array (pg_query ("select * from manufacturer where id = $id_manu"));

?>

<form method="post" action="recv_manu.php">
Name:<input type="text" name="name" value="<?= $row['name']?>" size="10"><p>
Name:<input type="text" name="code" value="<?= $row['code']?>" size="3">(2-letter abbreviation)<p>
Address:<P>
<textarea name="address" cols="30" rows="4"><?= $row['address'] ?></textarea>
Phone:<input type="text" name="phone" value="<?= $row['phone']?>" size="10"><p>
Fax:<input type="text" name="fax" value="<?= $row['fax']?>" size="10"><p>
Country:<input type="text" name="iso_countrycode" value="<?= $row['iso_countrycode']?>" size="3"><p>
Comment:<p>
<textarea name="comment" cols="30" rows="4"><?= $row['comment'] ?></textarea><p>
<input type="hidden" name="id_manu" value="<?= $id_manu ?>">
<input type="submit" value="submit"></form>
</body></html>