<?php
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
// or see online at http://www.gnu.org/licenses/gpl.html\


include ('connect.php');

pg_query ("update drug_element set description = '$name' where id=$id");
?>

<html><body>
<h2>Name Changed</h2>

<a href="viewelement.php?id=<?= $id ?>">Back</a>

</body></html>