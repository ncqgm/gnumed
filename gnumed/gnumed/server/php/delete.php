<?php
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
// or see online at http://www.gnu.org/licenses/gpl.html\


include ('connect.php');

pg_query ("delete from $table where id = $id");
?>

<html><body>
<h2>Deleted</h2>

<a href="<?= $ret ?>">Back</a>

</body></html>